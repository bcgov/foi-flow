"""Exercise the service's tracing without importing the database-backed API."""

import builtins
import importlib.util
from pathlib import Path

from flask import Flask, jsonify
from opentracing import Format
from opentracing.mocktracer import MockTracer
import jaeger_client
import pytest


@pytest.fixture
def tracing(monkeypatch):
    backend = MockTracer()
    configurations = []
    config_type = jaeger_client.Config

    def configure(**kwargs):
        configurations.append(kwargs)
        return config_type(**kwargs)

    monkeypatch.setattr(config_type, "initialize_tracer", lambda self: backend)
    monkeypatch.setattr(jaeger_client, "Config", configure)
    original_import = builtins.__import__

    def without_shared_tracing(name, *args, **kwargs):
        if name.split(".")[0] in {"sbc_common_components", "flask_opentracing"}:
            raise ImportError(f"{name} is deliberately absent")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_shared_tracing)
    path = Path(__file__).parents[1] / "request_api" / "tracer.py"
    spec = importlib.util.spec_from_file_location("service_tracer_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tracer, backend, configurations


def test_tracer_initializes_once_without_sbc_or_flask_opentracing(tracing):
    tracer_type, backend, configurations = tracing
    first = tracer_type.get_instance()
    assert tracer_type.get_instance() is first
    assert configurations == [{
        "service_name": "Authentication Services",
        "config": {
            "sampler": {"type": "const", "param": 1},
            "logging": True,
            "reporter_batch_size": 1,
            "trace_id_header": "registries-trace-id",
        },
    }]


@pytest.mark.parametrize("result,status", [
    ({"ok": True}, 200),
    (({"ok": True}, 201), 201),
    (("accepted", "202 ACCEPTED", {"X-Test": "preserved"}), 202),
    (("denied", 403), 403),
])
def test_traced_handler_preserves_return_value_and_records_http_status(tracing, result, status):
    tracer_type, backend, _ = tracing
    app = Flask(__name__)

    @tracer_type.get_instance().trace()
    def handler():
        return result

    with app.test_request_context("/requests", method="POST"):
        assert handler() is result
    span, = backend.finished_spans()
    assert span.tags["http.method"] == "POST"
    assert span.tags["http.url"] == "http://localhost/requests"
    assert span.tags["http.status_code"] == status
    assert span.tags["component"] == "Flask"
    assert span.tags["span.kind"] == "server"
    assert backend.active_span is None


def test_traced_route_preserves_response_and_parent_context(tracing):
    tracer_type, backend, _ = tracing
    app = Flask(__name__)

    @app.get("/requests")
    @tracer_type.get_instance().trace()
    def requests():
        response = jsonify({"id": 7})
        response.headers["X-Request"] = "preserved"
        return response

    parent = backend.start_span("upstream")
    headers = {}
    backend.inject(parent.context, Format.HTTP_HEADERS, headers)
    response = app.test_client().get("/requests", headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"id": 7}
    assert response.headers["X-Request"] == "preserved"
    child, = backend.finished_spans()
    assert child.operation_name == "requests"
    assert child.context.trace_id == parent.context.trace_id
    assert child.parent_id == parent.context.span_id
    assert backend.active_span is None


def test_handler_exception_is_reraised_and_span_is_finished(tracing):
    tracer_type, backend, _ = tracing
    app = Flask(__name__)
    failure = ValueError("document failed")

    @tracer_type.get_instance().trace()
    def handler():
        raise failure

    with app.test_request_context("/requests"):
        with pytest.raises(ValueError) as caught:
            handler()
    assert caught.value is failure
    span, = backend.finished_spans()
    assert span.tags["error"] is True
    assert span.tags["http.status_code"] == 500
    assert backend.active_span is None


def test_bad_parent_header_starts_a_new_span(tracing):
    tracer_type, backend, _ = tracing
    app = Flask(__name__)

    @app.get("/requests")
    @tracer_type.get_instance().trace()
    def requests():
        return jsonify({"id": 7})

    response = app.test_client().get("/requests", headers={"ot-tracer-traceid": "abc"})
    assert response.status_code == 200
    span, = backend.finished_spans()
    assert span.parent_id is None
    assert backend.active_span is None


def test_http_exception_preserves_status_and_closes_span(tracing):
    from werkzeug.exceptions import Forbidden

    tracer_type, backend, _ = tracing
    app = Flask(__name__)

    @app.get("/requests")
    @tracer_type.get_instance().trace()
    def requests():
        raise Forbidden()

    assert app.test_client().get("/requests").status_code == 403
    span, = backend.finished_spans()
    assert span.tags["error"] is True
    assert span.tags["http.status_code"] == 403
    assert backend.active_span is None
