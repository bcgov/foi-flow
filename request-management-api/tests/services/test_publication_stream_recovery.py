"""Test Redis group recovery without loading database-backed event handlers."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest
import redis


PUBLISH = "publication.publish.completed"
UNPUBLISH = "publication.unpublish.completed"
GROUP = "request-management-api"


class FakeRedisClient:
    def __init__(self):
        self.streams = {PUBLISH: [], UNPUBLISH: []}
        self.groups = {}
        self.acked = []

    def xgroup_create(self, name, groupname, id, mkstream):
        if (name, groupname) in self.groups:
            raise redis.exceptions.ResponseError("BUSYGROUP Consumer Group name already exists")
        if name not in self.streams:
            assert mkstream
            self.streams[name] = []
        self.groups[name, groupname] = len(self.streams[name]) if id == "$" else 0

    def xreadgroup(self, groupname, consumername, streams, count, block):
        for name in streams:
            if name not in self.streams or (name, groupname) not in self.groups:
                raise redis.exceptions.ResponseError(f"NOGROUP No such key '{name}' or consumer group")
        messages = []
        for name in streams:
            cursor = self.groups[name, groupname]
            entries = self.streams[name][cursor:cursor + count]
            self.groups[name, groupname] += len(entries)
            if entries:
                messages.append((name, entries))
        return messages

    def xack(self, name, groupname, message_id):
        self.acked.append((name, groupname, message_id))

    def add_event(self, name, message_id):
        self.streams[name].append((message_id, {"payload": {
            "event_id": message_id,
            "event_type": name,
            "payload": {"kind": "openinfo"},
        }}))


@pytest.fixture
def consumer(monkeypatch):
    # Only the handler import is stubbed; the production stream consumer is executed.
    handlers_module = ModuleType("request_api.services.publication_events.consumer")
    handlers_module.OpenInfoPublicationCompletedConsumer = object
    handlers_module.ProactiveDisclosurePublicationCompletedConsumer = object
    monkeypatch.setitem(sys.modules, handlers_module.__name__, handlers_module)
    path = Path(__file__).parents[2] / "request_api/services/publication_events/completed_stream_consumer.py"
    spec = importlib.util.spec_from_file_location("publication_stream_recovery_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    handled = []

    def handle(envelope):
        handled.append(envelope["event_id"])
        return SimpleNamespace(success=True)

    instance = module.PublicationCompletedStreamConsumer(
        redis_client=FakeRedisClient(),
        stream_names={PUBLISH: PUBLISH, UNPUBLISH: UNPUBLISH},
        group_name=GROUP,
        consumer_name="worker-1",
        handlers={"openinfo": SimpleNamespace(handle=handle)},
    )
    return instance, handled


@pytest.mark.parametrize("missing_stream", [PUBLISH, UNPUBLISH])
def test_recovery_skips_retained_events_and_consumes_future_events(consumer, missing_stream):
    instance, handled = consumer
    client = instance.redis_client
    instance.ensure_groups()
    client.add_event(missing_stream, "old-event")
    assert instance.read_once() == 1
    assert handled == ["old-event"]
    client.add_event(missing_stream, "outstanding-event")
    del client.groups[missing_stream, GROUP]

    assert instance.read_once() == 0
    assert instance.read_once() == 0
    assert handled == ["old-event"]

    client.add_event(missing_stream, "new-event")
    assert instance.read_once() == 1
    assert handled == ["old-event", "new-event"]
    assert client.acked[-1] == (missing_stream, GROUP, "new-event")


def test_recovery_preserves_backlog_for_existing_group(consumer):
    instance, handled = consumer
    instance.ensure_groups()
    instance.redis_client.add_event(UNPUBLISH, "outstanding-event")
    del instance.redis_client.groups[PUBLISH, GROUP]

    assert instance.read_once() == 0
    assert instance.read_once() == 1
    assert handled == ["outstanding-event"]


def test_recovery_recreates_deleted_stream(consumer):
    instance, handled = consumer
    instance.ensure_groups()
    del instance.redis_client.streams[PUBLISH]
    del instance.redis_client.groups[PUBLISH, GROUP]

    assert instance.read_once() == 0
    instance.redis_client.add_event(PUBLISH, "new-event")
    assert instance.read_once() == 1
    assert handled == ["new-event"]


def test_initial_group_creation_consumes_existing_events(consumer):
    instance, handled = consumer
    instance.redis_client.add_event(PUBLISH, "existing-event")

    instance.ensure_groups()

    assert instance.read_once() == 1
    assert handled == ["existing-event"]


def test_unrelated_redis_read_errors_propagate(consumer, monkeypatch):
    instance, _ = consumer

    def fail(**kwargs):
        raise redis.exceptions.ResponseError("WRONGTYPE invalid stream")

    monkeypatch.setattr(instance.redis_client, "xreadgroup", fail)

    with pytest.raises(redis.exceptions.ResponseError, match="WRONGTYPE"):
        instance.read_once()
    assert instance.redis_client.groups == {}


def test_group_recreation_errors_propagate_to_retry_loop(consumer, monkeypatch):
    instance, _ = consumer

    def fail(**kwargs):
        raise redis.exceptions.ResponseError("NOPERM group creation denied")

    monkeypatch.setattr(instance.redis_client, "xgroup_create", fail)

    with pytest.raises(redis.exceptions.ResponseError, match="NOPERM"):
        instance.read_once()
