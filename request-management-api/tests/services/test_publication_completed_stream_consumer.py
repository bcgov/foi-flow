import json

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.completed_stream_consumer import (
    PublicationCompletedStreamConsumer,
)
from request_api.services.publication_events.types import PublicationEventType


class FakeRedisClient:
    def __init__(self, messages=None):
        self.messages = messages or []
        self.created_groups = []
        self.acked = []

    def xgroup_create(self, name, groupname, id="0", mkstream=False):
        self.created_groups.append((name, groupname, id, mkstream))

    def xreadgroup(self, groupname, consumername, streams, count=None, block=None):
        if not self.messages:
            return []
        return self.messages.pop(0)

    def xack(self, stream_name, group_name, message_id):
        self.acked.append((stream_name, group_name, message_id))


class FakeHandler:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or DefaultMethodResult(True, "handled")

    def handle(self, envelope):
        self.calls.append(envelope)
        return self.result


def test_from_env_configures_completed_streams(monkeypatch):
    monkeypatch.setenv("OPENINFO_PUBLISH_COMPLETED_STREAM_NAME", "openinfo.publish.completed")
    monkeypatch.setenv(
        "PROACTIVEDISCLOSURE_PUBLISH_COMPLETED_STREAM_NAME",
        "proactivedisclosure.publish.completed",
    )
    monkeypatch.setenv("PUBLICATION_COMPLETED_CONSUMER_GROUP", "request-management-api")
    monkeypatch.setenv("PUBLICATION_COMPLETED_CONSUMER_NAME", "request-management-api-1")

    consumer = PublicationCompletedStreamConsumer.from_env(redis_client=FakeRedisClient())

    assert consumer.stream_names == {
        "openinfo.publish.completed": "openinfo.publish.completed",
        "proactivedisclosure.publish.completed": "proactivedisclosure.publish.completed",
    }
    assert consumer.group_name == "request-management-api"
    assert consumer.consumer_name == "request-management-api-1"


def test_ensure_groups_creates_configured_stream_groups():
    redis_client = FakeRedisClient()
    consumer = PublicationCompletedStreamConsumer(
        redis_client=redis_client,
        stream_names={
            PublicationEventType.OPENINFO_PUBLISH_COMPLETED: "openinfo.publish.completed",
            PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED: "proactivedisclosure.publish.completed",
        },
        group_name="request-management-api",
        consumer_name="worker-1",
    )

    consumer.ensure_groups()

    assert redis_client.created_groups == [
        ("openinfo.publish.completed", "request-management-api", "0", True),
        ("proactivedisclosure.publish.completed", "request-management-api", "0", True),
    ]


def test_read_once_dispatches_envelope_payload_and_acks_success():
    envelope = {
        "event_type": "openinfo.publish.completed",
        "correlation_id": "openinfo-publish-345",
        "payload": {"tenant_id": "tenant-1", "request_event_id": "request-event-1"},
    }
    redis_client = FakeRedisClient(
        messages=[
            [
                (
                    "openinfo.publish.completed",
                    [("1700000000000-0", {"payload": json.dumps(envelope)})],
                )
            ]
        ]
    )
    handler = FakeHandler()
    consumer = PublicationCompletedStreamConsumer(
        redis_client=redis_client,
        stream_names={PublicationEventType.OPENINFO_PUBLISH_COMPLETED: "openinfo.publish.completed"},
        group_name="request-management-api",
        consumer_name="worker-1",
        handlers={PublicationEventType.OPENINFO_PUBLISH_COMPLETED: handler},
    )

    processed = consumer.read_once()

    assert processed == 1
    assert handler.calls == [envelope]
    assert redis_client.acked == [
        ("openinfo.publish.completed", "request-management-api", "1700000000000-0")
    ]


def test_read_once_does_not_ack_failed_handler_result():
    envelope = {
        "event_type": "proactivedisclosure.publish.completed",
        "correlation_id": "proactivedisclosure-publish-71",
        "payload": {"tenant_id": "tenant-1", "request_event_id": "request-event-1"},
    }
    redis_client = FakeRedisClient(
        messages=[
            [
                (
                    "proactivedisclosure.publish.completed",
                    [("1700000000000-1", {"payload": json.dumps(envelope)})],
                )
            ]
        ]
    )
    handler = FakeHandler(DefaultMethodResult(False, "not found", 71))
    consumer = PublicationCompletedStreamConsumer(
        redis_client=redis_client,
        stream_names={
            PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED: "proactivedisclosure.publish.completed"
        },
        group_name="request-management-api",
        consumer_name="worker-1",
        handlers={PublicationEventType.PROACTIVE_DISCLOSURE_PUBLISH_COMPLETED: handler},
    )

    processed = consumer.read_once()

    assert processed == 1
    assert handler.calls == [envelope]
    assert redis_client.acked == []
