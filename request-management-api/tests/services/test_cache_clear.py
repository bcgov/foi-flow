import fnmatch

import pytest
import redis

from request_api.utils import cache


class FakeRedisClient:
    def __init__(self, entries=None):
        self.entries = dict(entries or {})
        self.deleted_batches = []

    def scan_iter(self, match, count):
        for key in list(self.entries):
            if fnmatch.fnmatch(key, match):
                yield key

    def delete(self, *keys):
        self.deleted_batches.append(keys)
        deleted = 0
        for key in keys:
            if key in self.entries:
                del self.entries[key]
                deleted += 1
        return deleted

    def flushall(self):
        self.entries.clear()


@pytest.fixture
def redis_client(monkeypatch):
    client = FakeRedisClient()
    monkeypatch.setattr(cache, "cache_client", client)
    monkeypatch.setenv("CACHE_ENABLED", "Y")
    return client


def test_clear_cache_preserves_publication_streams_and_other_keys(redis_client):
    stream = {"messages": ["completed-event"], "groups": ["request-management-api"]}
    redis_client.entries.update({
        "foi_cache_subjectcodes83e0459e": "cached subjects",
        "foi_cache_view//api/foiflow/divisions/CAF221cc66d": "cached divisions",
        "flask_cache_legacy": "legacy cache",
        "publication.publish.completed": stream,
        "publication.unpublish.completed": stream,
        "foirequest-dedupe:abc": "request hash",
    })

    assert cache.clear_cache() is True

    assert redis_client.entries == {
        "flask_cache_legacy": "legacy cache",
        "publication.publish.completed": stream,
        "publication.unpublish.completed": stream,
        "foirequest-dedupe:abc": "request hash",
    }


@pytest.mark.parametrize("key_count", [0, 1, 100, 205])
def test_clear_cache_removes_all_matching_keys_in_bounded_batches(redis_client, key_count):
    redis_client.entries.update({f"foi_cache_item{i}": "cached" for i in range(key_count)})

    assert cache.clear_cache() is True

    assert redis_client.entries == {}
    assert all(1 <= len(batch) <= 100 for batch in redis_client.deleted_batches)
    assert sum(len(batch) for batch in redis_client.deleted_batches) == key_count


def test_clear_cache_uses_configured_prefix(redis_client, monkeypatch):
    monkeypatch.setattr(cache.Config, "CACHE_KEY_PREFIX", "custom_cache_", raising=False)
    redis_client.entries.update({"custom_cache_item": "cached", "flask_cache_other": "other"})

    assert cache.clear_cache() is True

    assert redis_client.entries == {"flask_cache_other": "other"}


def test_clear_cache_does_not_access_redis_when_disabled(redis_client, monkeypatch):
    monkeypatch.setenv("CACHE_ENABLED", "N")
    redis_client.entries["foi_cache_item"] = "cached"

    def unexpected_scan(**kwargs):
        pytest.fail("Disabled caching must not scan Redis")

    monkeypatch.setattr(redis_client, "scan_iter", unexpected_scan)

    assert cache.clear_cache() is True
    assert redis_client.entries == {"foi_cache_item": "cached"}


@pytest.mark.parametrize("operation", ["scan_iter", "delete"])
def test_clear_cache_returns_false_and_logs_traceback_on_redis_failure(
    redis_client, monkeypatch, caplog, operation
):
    redis_client.entries["foi_cache_item"] = "cached"

    def fail(*args, **kwargs):
        raise redis.exceptions.ConnectionError("Redis unavailable")

    monkeypatch.setattr(redis_client, operation, fail)

    assert cache.clear_cache() is False
    assert any(record.exc_info for record in caplog.records)
