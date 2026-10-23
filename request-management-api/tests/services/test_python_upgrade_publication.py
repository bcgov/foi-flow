"""Verify the existing stream acknowledgement semantics against disposable Redis."""

import json
import os
import uuid
import subprocess
import sys
from pathlib import Path

import pytest
import redis

from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.publication_events.completed_stream_consumer import PublicationCompletedStreamConsumer
from test_python_upgrade_startup import synthetic_environment


@pytest.fixture
def stream():
    client = redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
    name = 'upgrade-completed-' + uuid.uuid4().hex
    yield client, name
    client.delete(name)


class Handler:
    def __init__(self, success):
        self.success = success
        self.seen = []

    def handle(self, envelope):
        self.seen.append(envelope['event_id'])
        return DefaultMethodResult(self.success, 'synthetic handler result')


def consumer(client, name, handler):
    return PublicationCompletedStreamConsumer(
        client, {'publication.publish.completed': name}, 'upgrade-group',
        'upgrade-worker', handlers={'openinfo': handler}, block_ms=1,
    )


def publish(client, name, event_id):
    return client.xadd(name, {'payload': json.dumps({
        'event_id': event_id, 'event_type': 'publication.publish.completed',
        'payload': {'kind': 'openinfo'},
    })})


def test_completed_event_is_acknowledged_after_success(stream):
    client, name = stream
    handler = Handler(True)
    worker = consumer(client, name, handler)
    worker.ensure_groups()
    publish(client, name, 'first')
    assert worker.read_once() == 1
    assert handler.seen == ['first']
    assert client.xpending(name, 'upgrade-group')['pending'] == 0


def test_handler_failure_remains_pending_after_restart(stream):
    client, name = stream
    handler = Handler(False)
    worker = consumer(client, name, handler)
    worker.ensure_groups()
    message_id = publish(client, name, 'failed')
    assert worker.read_once() == 1
    restarted = consumer(client, name, Handler(True))
    restarted.ensure_groups()
    assert restarted.read_once() == 0
    assert client.xpending_range(name, 'upgrade-group', min='-', max='+', count=10)[0]['message_id'] == message_id


def test_missing_group_recovery_preserves_skip_existing_behavior(stream):
    client, name = stream
    handler = Handler(True)
    publish(client, name, 'old')
    worker = consumer(client, name, handler)
    assert worker.read_once() == 0
    publish(client, name, 'new')
    assert worker.read_once() == 1
    assert handler.seen == ['new']


def test_background_workers_persist_publication_and_acknowledge(db):
    service_dir = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, 'tests/support/publication_background.py'], cwd=service_dir,
        env=synthetic_environment(), capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
