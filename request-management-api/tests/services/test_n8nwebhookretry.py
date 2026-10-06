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

    def register_script(self, script):
        """Python stand-in for the Lua claim script: lease due members by
        pushing their score to ARGV[3] and return them."""
        def claim(keys, args):
            name, now, limit, leaseuntil = keys[0], float(args[0]), int(args[1]), float(args[2])
            due = self.zrangebyscore(name, "-inf", now, start=0, num=limit)
            for member in due:
                self.zsets[name][member] = leaseuntil
            return due
        return claim


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
    assert failed[0]["id"] == "a"
    assert failed[0]["lasterror"] == "HTTP 500"
    assert "needs operator action" in caplog.text


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
    assert failed["lasterror"] == "HTTP 401"
    assert failed["attempts"] == 2


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
    assert failed["payload"] == PAYLOAD
    assert failed["attempts"] == 1
    assert failed["lasterror"] == "HTTP 503"


def test_backlog_reports_pending_and_failed_sizes(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "payload": PAYLOAD}): 999.0})
    queue.deadletterpayload(PAYLOAD)
    assert queue.backlog() == (1, 1)


def test_scheduler_logs_backlog_when_not_empty(queue, redis_client, caplog):
    caplog.set_level("INFO")
    redis_client.zadd(queue.queuename, {json.dumps({"id": "later", "payload": PAYLOAD}): 9e18})
    N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: FakeEngine()).run_once()
    assert "n8n webhook retry backlog; pending=1 failed=0" in caplog.text


def test_claimdue_leases_due_entries_instead_of_removing_them(queue, redis_client):
    due = json.dumps({"id": "due", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {due: 50.0, json.dumps({"id": "later", "payload": PAYLOAD}): 500.0})
    claimed = queue.claimdue(limit=10, now=100.0)
    assert [(member, entry["id"]) for member, entry in claimed] == [(due, "due")]
    assert redis_client.zsets[queue.queuename][due] == 100.0 + queue.leaseseconds


def test_second_claim_before_lease_ends_gets_nothing(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "payload": PAYLOAD}): 0.0})
    assert len(queue.claimdue(now=100.0)) == 1
    assert queue.claimdue(now=100.0 + queue.leaseseconds - 1) == []


def test_unacked_entry_becomes_due_again_after_lease(queue, redis_client):
    """Simulates a pod dying between claim and ack: nothing is lost."""
    original = {"id": "a", "attempts": 2, "payload": dict(PAYLOAD, eventId="e-1")}
    redis_client.zadd(queue.queuename, {json.dumps(original): 0.0})
    queue.claimdue(now=100.0)
    (member, entry), = queue.claimdue(now=100.0 + queue.leaseseconds + 1)
    assert entry == original


def test_ack_removes_the_leased_member(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "payload": PAYLOAD}): 0.0})
    (member, _), = queue.claimdue(now=100.0)
    queue.ack(member)
    assert _pending(redis_client, queue) == {}


def test_reschedule_replaces_the_leased_member_with_one_new_entry(queue, redis_client, monkeypatch):
    monkeypatch.setattr("request_api.services.external.n8nwebhookretryqueue.time.time", lambda: 1000.0)
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "attempts": 1, "payload": PAYLOAD}): 0.0})
    (member, entry), = queue.claimdue(now=100.0)
    assert queue.reschedule(member, entry, 2, "HTTP 503") is True
    pending = _pending(redis_client, queue)
    assert list(pending) == ["a"]
    assert pending["a"][0]["attempts"] == 2
    assert pending["a"][0]["lasterror"] == "HTTP 503"
    assert pending["a"][1] == 1060.0


def test_reschedule_dead_letters_at_max_attempts(queue, redis_client):
    redis_client.zadd(queue.queuename, {json.dumps({"id": "a", "attempts": 4, "payload": PAYLOAD}): 0.0})
    (member, entry), = queue.claimdue(now=100.0)
    assert queue.reschedule(member, entry, 5, "HTTP 500") is False
    assert _pending(redis_client, queue) == {}
    assert json.loads(redis_client.lists[queue.deadlettername][0])["attempts"] == 5


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_invalid_lease_seconds_falls_back_to_default(redis_client, monkeypatch, value):
    monkeypatch.setenv("N8N_WEBHOOK_RETRY_LEASE_SECONDS", value)
    assert n8nwebhookretryqueue(redisclient=redis_client).leaseseconds == 300


def test_corrupt_member_is_dead_lettered_and_others_still_claimed(queue, redis_client):
    good = json.dumps({"id": "good", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {"not-json{": 0.0, good: 1.0})
    claimed = queue.claimdue(now=100.0)
    assert [entry["id"] for _, entry in claimed] == ["good"]
    assert "not-json{" not in redis_client.zsets[queue.queuename]
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["lasterror"] == "invalid JSON"
    assert failed["raw"] == "not-json{"


class RaisingEngine:
    def __init__(self, *results):
        self.results = list(results)

    def deliver(self, payload):
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_scheduler_reschedules_entry_whose_delivery_raises_and_continues(queue, redis_client):
    _due_entry(redis_client, queue, attempts=1, entryid="boom")
    _due_entry(redis_client, queue, attempts=1, entryid="ok")
    engine = RaisingEngine(RuntimeError("bug"), n8ndeliveryresult(True, content={}))
    assert N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once() == 1
    pending = _pending(redis_client, queue)
    assert list(pending) == ["boom"]
    assert pending["boom"][0]["attempts"] == 2
    assert pending["boom"][0]["lasterror"] == "RuntimeError"


def test_entry_stays_leased_when_ack_fails_after_delivery(queue, redis_client, monkeypatch):
    _due_entry(redis_client, queue, attempts=1)
    monkeypatch.setattr(queue, "ack", lambda member: (_ for _ in ()).throw(ConnectionError("redis down")))
    engine = FakeEngine(n8ndeliveryresult(True, content={}))
    with pytest.raises(ConnectionError):
        N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once()
    assert list(_pending(redis_client, queue)) == ["a"]


def test_check_lease_warns_when_lease_is_shorter_than_a_batch(queue, caplog, monkeypatch):
    monkeypatch.setattr(queue, "leaseseconds", 50)
    N8NWebhookRetryScheduler(queue=queue, batch_size=10, webhook_timeout_seconds=10).check_lease()
    assert "lease is not longer than a worst-case batch" in caplog.text


def test_check_lease_is_quiet_when_lease_is_long_enough(queue, caplog):
    N8NWebhookRetryScheduler(queue=queue, batch_size=10, webhook_timeout_seconds=10).check_lease()
    assert "lease is not longer" not in caplog.text


def test_scheduler_from_env_reads_webhook_timeout(monkeypatch, queue):
    monkeypatch.setenv("N8N_WEBHOOK_TIMEOUT_SECONDS", "4")
    assert N8NWebhookRetryScheduler.from_env(queue=queue).webhook_timeout_seconds == 4.0


@pytest.mark.parametrize("member", ["123", "[]", "null"])
def test_non_object_member_is_dead_lettered_and_others_still_claimed(queue, redis_client, member):
    good = json.dumps({"id": "good", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {member: 0.0, good: 1.0})
    claimed = queue.claimdue(now=100.0)
    assert [entry["id"] for _, entry in claimed] == ["good"]
    assert member not in redis_client.zsets[queue.queuename]
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["lasterror"] == "invalid entry"
    assert failed["raw"] == member


def test_scheduler_dead_letters_entry_with_non_numeric_attempts_and_continues(queue, redis_client):
    bad = json.dumps({"id": "bad", "event": PAYLOAD["event"], "attempts": "x", "payload": PAYLOAD})
    redis_client.zadd(queue.queuename, {bad: 0.0})
    _due_entry(redis_client, queue, attempts=1, entryid="ok")
    engine = FakeEngine(n8ndeliveryresult(True, content={}))
    assert N8NWebhookRetryScheduler(queue=queue, engine_factory=lambda: engine).run_once() == 1
    assert _pending(redis_client, queue) == {}
    failed = json.loads(redis_client.lists[queue.deadlettername][0])
    assert failed["id"] == "bad"
    assert failed["lasterror"] == "invalid attempts"
