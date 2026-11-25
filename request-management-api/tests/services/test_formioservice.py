"""FOIMOD-5525: Form.io client (limited-user login, token cache, error mapping). All data is made up."""
import importlib.util
import sys
import threading

import pytest
import requests
from jose import jwt

from request_api.services.external import formioservice as formioservice_module
from request_api.services.external.formioservice import (
    FormioError,
    FormioNotConfigured,
    FormioNotFound,
    formioservice,
    reset_cache,
)

URL = "https://formio.test"
EMAIL = "limited@example.test"
PASSWORD = "p4ssw0rd-made-up"
NOW = 1_000_000.0


def _token(exp=None, marker="a"):
    claims = {"m": marker}
    if exp is not None:
        claims["exp"] = exp
    return jwt.encode(claims, "k", algorithm="HS256")


@pytest.fixture(autouse=True)
def _settings(monkeypatch):
    monkeypatch.setenv("FORMIO_URL", URL)
    monkeypatch.setenv("FORMIO_PAYMENT_USER_EMAIL", EMAIL)
    monkeypatch.setenv("FORMIO_PAYMENT_USER_PASSWORD", PASSWORD)
    monkeypatch.setattr(formioservice_module, "_now", lambda: NOW)
    reset_cache()
    yield
    reset_cache()


def _login(requests_mock, token=None):
    token = token or _token(NOW + 3600)
    return requests_mock.post(URL + "/user/login", headers={"x-jwt-token": token}, json={}), token


@pytest.mark.parametrize("name", ["FORMIO_URL", "FORMIO_PAYMENT_USER_EMAIL", "FORMIO_PAYMENT_USER_PASSWORD"])
@pytest.mark.parametrize("blank", [None, ""])
def test_missing_settings_raise_not_configured(monkeypatch, name, blank):
    if blank is None:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, blank)
    with pytest.raises(FormioNotConfigured) as exc:
        formioservice()._request("GET", "/payfeeonline")
    assert name in str(exc.value)
    assert PASSWORD not in str(exc.value)


def test_login_posts_credentials_and_uses_jwt_header(requests_mock):
    login, token = _login(requests_mock)
    get = requests_mock.get(URL + "/payfeeonline", json={})
    resp = formioservice()._request("GET", "/payfeeonline")
    assert resp.status_code == 200
    assert login.last_request.json() == {"data": {"email": EMAIL, "password": PASSWORD}}
    assert get.last_request.headers["x-jwt-token"] == token


def test_token_reused_until_60s_before_exp(requests_mock, monkeypatch):
    exp = NOW + 3600
    login, _ = _login(requests_mock, _token(exp))
    requests_mock.get(URL + "/payfeeonline", json={})
    svc = formioservice()
    svc._request("GET", "/payfeeonline")
    svc._request("GET", "/payfeeonline")
    assert login.call_count == 1
    monkeypatch.setattr(formioservice_module, "_now", lambda: exp - 61)
    svc._request("GET", "/payfeeonline")
    assert login.call_count == 1
    monkeypatch.setattr(formioservice_module, "_now", lambda: exp - 30)
    svc._request("GET", "/payfeeonline")
    assert login.call_count == 2


def test_token_without_exp_cached_300_seconds(requests_mock, monkeypatch):
    login, _ = _login(requests_mock, _token(None))
    requests_mock.get(URL + "/payfeeonline", json={})
    svc = formioservice()
    svc._request("GET", "/payfeeonline")
    monkeypatch.setattr(formioservice_module, "_now", lambda: NOW + 200)
    svc._request("GET", "/payfeeonline")
    assert login.call_count == 1
    monkeypatch.setattr(formioservice_module, "_now", lambda: NOW + 300)
    svc._request("GET", "/payfeeonline")
    assert login.call_count == 2


def test_login_without_token_header_raises(requests_mock):
    requests_mock.post(URL + "/user/login", json={})
    with pytest.raises(FormioError):
        formioservice()._request("GET", "/payfeeonline")


@pytest.mark.parametrize("status", [440, 401])
def test_relogins_once_on_expired_session(requests_mock, status):
    login, _ = _login(requests_mock)
    get = requests_mock.get(URL + "/payfeeonline", [{"status_code": status}, {"status_code": 200}])
    assert formioservice()._request("GET", "/payfeeonline").status_code == 200
    assert login.call_count == 2 and get.call_count == 2


@pytest.mark.parametrize("status", [440, 401])
def test_gives_up_after_one_relogin(requests_mock, status):
    login, _ = _login(requests_mock)
    get = requests_mock.get(URL + "/payfeeonline", [{"status_code": status}, {"status_code": status}])
    with pytest.raises(FormioError):
        formioservice()._request("GET", "/payfeeonline")
    assert login.call_count == 2 and get.call_count == 2


def test_concurrent_first_calls_log_in_once(requests_mock):
    login, _ = _login(requests_mock)
    requests_mock.get(URL + "/payfeeonline", json={})
    barrier = threading.Barrier(5)
    results, errors = [], []

    def work():
        try:
            barrier.wait()
            results.append(formioservice()._request("GET", "/payfeeonline").status_code)
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=work) for _ in range(5)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors and results == [200] * 5
    assert login.call_count == 1


def test_errors_hide_response_body_and_secrets(requests_mock, caplog):
    _, token = _login(requests_mock)
    requests_mock.get(URL + "/boom", status_code=500, text="SECRET-BODY")
    requests_mock.get(URL + "/slow", exc=requests.exceptions.ConnectTimeout(f"{PASSWORD} {token}"))
    svc = formioservice()
    with caplog.at_level("DEBUG"):
        with pytest.raises(FormioError) as e1:
            svc._request("GET", "/boom")
        with pytest.raises(FormioError) as e2:
            svc._request("GET", "/slow")
    assert str(e1.value) == "Form.io GET returned 500"
    assert str(e2.value) == "Form.io unreachable"
    for text in (str(e1.value), str(e2.value), caplog.text):
        assert "SECRET-BODY" not in text and PASSWORD not in text and token not in text


def test_login_failure_hides_secrets(requests_mock):
    requests_mock.post(URL + "/user/login", status_code=401, text="SECRET-BODY")
    with pytest.raises(FormioError) as exc:
        formioservice()._request("GET", "/payfeeonline")
    assert "SECRET-BODY" not in str(exc.value) and PASSWORD not in str(exc.value)


def test_404_raises_formio_not_found(requests_mock):
    _login(requests_mock)
    requests_mock.get(URL + "/nope", status_code=404)
    with pytest.raises(FormioNotFound):
        formioservice()._request("GET", "/nope")
    assert issubclass(FormioNotFound, FormioError)


def test_request_uses_timeout(requests_mock):
    _login(requests_mock)
    get = requests_mock.get(URL + "/payfeeonline", json={})
    formioservice()._request("GET", "/payfeeonline")
    assert get.last_request.timeout == (10, 10)


def test_import_does_no_network(requests_mock):
    # Load a throwaway copy: reloading the real module would rebind its exception classes and lock.
    spec = importlib.util.spec_from_file_location("formioservice_import_check", formioservice_module.__file__)
    module = importlib.util.module_from_spec(spec)
    before = sys.modules[formioservice_module.__name__]
    spec.loader.exec_module(module)
    assert requests_mock.call_count == 0
    assert module.FormioError is not FormioError
    assert sys.modules[formioservice_module.__name__] is before
    assert formioservice_module.FormioError is FormioError
