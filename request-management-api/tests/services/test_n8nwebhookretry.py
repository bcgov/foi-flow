import json

import pytest

from request_api.services.external.commonworkflowservice import n8ndeliveryresult
from request_api.services.external.n8nwebhookretryqueue import n8nwebhookretryqueue, retryenabled
from request_api.services.n8nwebhookretryscheduler import N8NWebhookRetryScheduler


class FakePipeline:
    """Queues commands and applies them together on execute(), like MULTI/EXEC."""

    def __init__(self, client):
        self.client = client
        self.commands = []

    def __getattr__(self, name):
        def queue(*args, **kwargs):
            self.commands.append((name, args, kwargs))
            return self
        return queue

    def execute(self):
        return [getattr(self.client, name)(*args, **kwargs) for name, args, kwargs in self.commands]


class FakeRedisClient:
    """Just the sorted-set and list commands the retry queue uses."""

    def __init__(self):
        self.zsets = {}
        self.lists = {}

    def zadd(self, name, mapping):
        self.zsets.setdefault(name, {}).update(mapping)
        return len(mapping)

    def zrangebyscore(self, name, minimum, maximum, start=0, num=None):
        members = sorted((score, member) for member, score in self.zsets.get(name, {}).items() if score <= float(maximum))
        members = [member for _, member in members][start:]
        return members[:num] if num is not None else members

    def zrem(self, name, member):
        return 1 if self.zsets.get(name, {}).pop(member, None) is not None else 0

    def zcard(self, name):
        return len(self.zsets.get(name, {}))

    def rpush(self, name, value):
        self.lists.setdefault(name, []).append(value)
        return len(self.lists[name])

    def ltrim(self, name, start, end):
        items = self.lists.get(name, [])
        size = len(items)
        first = start + size if start < 0 else start
        last = end + size if end < 0 else end
        self.lists[name] = items[max(first, 0):last + 1]
        return True

    def llen(self, name):
        return len(self.lists.get(name, []))

    def pipeline(self, transaction=True):
        return FakePipeline(self)


class FakeEngine:
    def __init__(self, *results):
        self.results = list(results)
        self.payloads = []

    def deliver(self, payload):
        self.payloads.append(payload)
        return self.results.pop(0)


@pytest.fixture(autouse=True)
def _retry_env(monkeypatch):
    for name in ("N8N_WEBHOOK_RETRY_QUEUE", "N8N_WEBHOOK_RETRY_MAX_ATTEMPTS",
                 "N8N_WEBHOOK_RETRY_BACKOFF_SECONDS", "N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS",
                 "N8N_WEBHOOK_RETRY_ENABLED", "N8N_WEBHOOK_DEADLETTER_MAX",
                 "N8N_WEBHOOK_RETRY_LEASE_SECONDS", "N8N_WEBHOOK_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def redis_client():
    return FakeRedisClient()


@pytest.fixture
def queue(redis_client):
    return n8nwebhookretryqueue(redisclient=redis_client)


PAYLOAD = {"event": "foi-intake-complete", "foiRequestMetaData": "{}"}


def _pending(redis_client, queue):
    return {json.loads(member)["id"]: (json.loads(member), score) for member, score in redis_client.zsets.get(queue.queuename, {}).items()}


def test_enqueue_schedules_retry_with_exponential_backoff(queue, redis_client, monkeypatch):
    monkeypatch.setattr("request_api.services.external.n8nwebhookretryqueue.time.time", lambda: 1000.0)
    assert queue.enqueue(PAYLOAD, attempts=1, error="Timeout", entryid="a") is True
    assert queue.enqueue(PAYLOAD, attempts=3, error="HTTP 503", entryid="b") is True
    pending = _pending(redis_client, queue)
    assert pending["a"][1] == 1030.0
    assert pending["b"][1] == 1120.0
    assert pending["a"][0]["payload"] == PAYLOAD
    assert pending["a"][0]["event"] == "foi-intake-complete"


def test_backoff_is_capped(redis_client, monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS", "20")
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS", "600")
    monkeypatch.setattr("request_api.services.external.n8nwebhookretryqueue.time.time", lambda: 0.0)
    queue = n8nwebhookretryqueue(redisclient=redis_client)
    queue.enqueue(PAYLOAD, attempts=10, entryid="a")
    assert _pending(redis_client, queue)["a"][1] == 600.0


def test_enqueue_dead_letters_when_attempts_are_exhausted(queue, redis_client, caplog):
    assert queue.enqueue(PAYLOAD, attempts=5, error="HTTP 500", entryid="a") is False
    assert queue.queuename not in redis_client.zsets
    failed = [json.loads(entry) for entry in redis_client.lists[queue.deadlettername]]
    assert failed[0]["id"] == "a" and failed[0]["lasterror"] == "HTTP 500"
    assert "needs operator action" in caplog.text


def test_claimdue_returns_only_due_entries_and_removes_them(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "due", "payload": PAYLOAD}): 50.0,
                                        json.dumps({"id": "later", "payload": PAYLOAD}): 500.0})
    claimed = queue.claimdue(limit=10, now=100.0)
    assert [entry["id"] for entry in claimed] == ["due"]
    assert list(_pending(redis_client, queue)) == ["later"]
    assert queue.claimdue(limit=10, now=100.0) == []


def test_claimdue_skips_entries_already_claimed_by_another_worker(queue, redis_client, monkeypatch):
    member = json.dumps({"id": "a", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {member: 0.0})
    monkeypatch.setattr(redis_client, "zrem", lambda name, value: 0)
    assert queue.claimdue(now=100.0) == []


def _due_entry(redis_client, queue, attempts=1, entryid="a"):
    redis_client.zadd(queue.queuename, {json.dumps({"id": entryid, "event": PAYLOAD["event"], "attempts": attempts, "payload": PAYLOAD}): 0.0})


def test_scheduler_delivers_due_entry(queue, redis_client):
    _due_entry(redis_client, queue)
    engine = FakeEngine(n8ndeliveryresult(True, content={}))
    scheduler = N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine)
    assert scheduler.run_once() == 1
    assert engine.payloads == [PAYLOAD]
    assert _pending(redis_client, queue) == {}
    assert queue.deadlettername not in redis_client.lists


def test_scheduler_requeues_retryable_failure_with_same_id(queue, redis_client):
    _due_entry(redis_client, queue, attempts=1)
    engine = FakeEngine(n8ndeliveryresult(False, retryable=True, error="HTTP 503"))
    N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once()
    entry, _ = _pending(redis_client, queue)["a"]
    assert entry["attempts"] == 2
    assert entry["lasterror"] == "HTTP 503"


def test_scheduler_dead_letters_after_last_attempt(queue, redis_client):
    _due_entry(redis_client, queue, attempts=4)
    engine = FakeEngine(n8ndeliveryresult(False, retryable=True, error="ConnectionError"))
    N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once()
    assert _pending(redis_client, queue) == {}
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["attempts"] == 5


def test_scheduler_dead_letters_non_retryable_failure(queue, redis_client):
    _due_entry(redis_client, queue, attempts=1)
    engine = FakeEngine(n8ndeliveryresult(False, retryable=False, error="HTTP 401"))
    N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once()
    assert _pending(redis_client, queue) == {}
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["lasterror"] == "HTTP 401" and failed["attempts"] == 2


def test_scheduler_from_env(monkeypatch, queue):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_INTERVAL_SECONDS", "15")
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_BATCH_SIZE", "3")
    scheduler = N8NWebhookRetryScheduler.from_env(queue=queue)
    assert scheduler.interval_seconds == 15
    assert scheduler.batch_size == 3


@pytest.mark.parametrize("value, expected", [
    (None, True), ("true", True), (" TRUE ", True),
    ("false", False), ("False", False), ("0", False),
])
def test_retryenabled(monkeypatch, value, expected):
    if value is None:
        monkeypatch.delenv("N8N_WEBHOOK_RETRY_ENABLED", raising=False)
    else:
        monkeypatch.setenv("N8N_WEBHOOK_RETRY_ENABLED", value)
    assert retryenabled() is expected


def test_deadletter_list_is_capped_keeping_newest(redis_client, monkeypatch, caplog):
    monkeypatch.setenv("N8N_WEBHOOK_DEADLETTER_MAX", "3")
    queue = n8nwebhookretryqueue(redisclient=redis_client)
    for index in range(5):
        queue.deadletter({"id": str(index), "event": "e", "attempts": 5, "lasterror": "HTTP 500", "payload": PAYLOAD})
    kept = [json.loads(entry)["id"] for entry in redis_client.lists[queue.deadlettername]]
    assert kept == ["2", "3", "4"]
    assert "dead-letter list is full" in caplog.text


@pytest.mark.parametrize("value", ["0", "-5", "abc"])
def test_invalid_deadletter_max_falls_back_to_default(redis_client, monkeypatch, value):
    monkeypatch.setenv("N8N_WEBHOOK_DEADLETTER_MAX", value)
    assert n8nwebhookretryqueue(redisclient=redis_client).deadlettermax == 1000


def test_deadletter_with_member_removes_it_from_the_queue(queue, redis_client):
    member = json.dumps({"id": "a", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {member: 0.0})
    queue.deadletter({"id": "a", "payload": PAYLOAD}, member)
    assert _pending(redis_client, queue) == {}
    assert len(redis_client.lists[queue.deadlettername]) == 1


def test_deadletterpayload_writes_straight_to_the_dead_letter_list(queue, redis_client):
    queue.deadletterpayload(PAYLOAD, attempts=1, error="HTTP 503")
    assert _pending(redis_client, queue) == {}
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["payload"] == PAYLOAD and failed["attempts"] == 1 and failed["lasterror"] == "HTTP 503"


def test_backlog_reports_pending_and_failed_sizes(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "payload": PAYLOAD}): 999.0})
    queue.deadletterpayload(PAYLOAD)
    assert queue.backlog() == (1, 1)


def test_scheduler_logs_backlog_when_not_empty(queue, redis_client, caplog):
    caplog.set_level("INFO")
    redis_client.zadd(queue.queuename, {json.dumps({"id": "later", "payload": PAYLOAD}): 9e18})
    N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: FakeEngine()).run_once()
    assert "n8n webhook retry backlog; pending=1 failed=0" in caplog.text
