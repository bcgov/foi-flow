import json
import logging
import os
import time
import uuid

import redis

"""
Delayed retry queue for n8n webhook events that could not be delivered
(network error, timeout, HTTP 429 or 5xx).

Pending entries live in a Redis sorted set (N8N_WEBHOOK_RETRY_QUEUE) scored
by the time of their next attempt. claimdue() leases due entries for
N8N_WEBHOOK_RETRY_LEASE_SECONDS instead of removing them, so an entry claimed
by a worker that dies is retried once the lease expires. Delivery is therefore
at-least-once; n8n must skip an eventId it has already completed. Entries
that exhaust N8N_WEBHOOK_RETRY_MAX_ATTEMPTS, fail with a non-retryable error,
or fail while N8N_WEBHOOK_RETRY_ENABLED is false move to the "<queue>:failed" list,
which keeps only the newest N8N_WEBHOOK_DEADLETTER_MAX entries.

Uses the EVENT_QUEUE_* Redis connection already configured for this API.

Operator notes (default queue name shown):
  Count failed events:   redis-cli LLEN foi-n8n-webhook-retry:failed
  Inspect newest 10:     redis-cli LRANGE foi-n8n-webhook-retry:failed -10 -1
  Replay one event:      copy its JSON entry, set "attempts" to 0, then
                         redis-cli ZADD foi-n8n-webhook-retry 0 '<entry json>'
                         and remove it from the list with
                         redis-cli LREM foi-n8n-webhook-retry:failed 1 '<original entry json>'
  Clear the list:        redis-cli DEL foi-n8n-webhook-retry:failed
"""

# Atomically finds up to ARGV[2] members due by ARGV[1] and leases them by
# pushing their score to ARGV[3], so no other worker sees them as due until
# the lease expires. Members stay in the zset until ack/reschedule/deadletter.
CLAIM_SCRIPT = """
local due = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1], 'LIMIT', 0, ARGV[2])
for _, m in ipairs(due) do redis.call('ZADD', KEYS[1], 'XX', ARGV[3], m) end
return due
"""


def retryenabled():
    """Single source of truth for N8N_WEBHOOK_RETRY_ENABLED (unset means enabled)."""
    return (os.getenv("N8N_WEBHOOK_RETRY_ENABLED") or "true").strip().lower() == "true"


def positiveint(name, default):
    """Reads a positive integer env var; unset, non-numeric or < 1 falls back to default."""
    try:
        value = int(os.getenv(name) or default)
    except ValueError:
        logging.warning("n8nwebhookretryqueue: %s=%r is not a number; using %s", name, os.getenv(name), default)
        return default
    return value if value >= 1 else default


class n8nwebhookretryqueue:

    def __init__(self, redisclient=None):
        self.queuename = os.getenv("N8N_WEBHOOK_RETRY_QUEUE") or "foi-n8n-webhook-retry"
        self.deadlettername = self.queuename + ":failed"
        self.maxattempts = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS") or 5)
        self.backoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_BACKOFF_SECONDS") or 30)
        self.maxbackoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS") or 3600)
        self.deadlettermax = positiveint("N8N_WEBHOOK_DEADLETTER_MAX", 1000)
        self.leaseseconds = positiveint("N8N_WEBHOOK_RETRY_LEASE_SECONDS", 300)
        self.redis = redisclient or redis.Redis(
            host=os.getenv("EVENT_QUEUE_HOST") or "localhost",
            port=int(os.getenv("EVENT_QUEUE_PORT") or 6379),
            password=os.getenv("EVENT_QUEUE_PASSWORD") or None,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        self._claimscript = self.redis.register_script(CLAIM_SCRIPT)

    def enqueue(self, payload, attempts=1, error=None, entryid=None):
        """Schedules the next attempt for an event that has already been tried
        `attempts` times. Returns False when the entry was dead-lettered instead."""
        entry = self.__newentry(payload, attempts, error, entryid)
        if attempts >= self.maxattempts:
            self.deadletter(entry)
            return False
        nextattemptat = time.time() + self.__backoff(attempts)
        self.redis.zadd(self.queuename, {json.dumps(entry): nextattemptat})
        logging.warning("n8nwebhookretryqueue: queued n8n event for retry; id=%s event=%s attempts=%s error=%s",
                        entry["id"], entry["event"], attempts, error)
        return True

    def deadletterpayload(self, payload, attempts=1, error=None):
        """Writes an event straight to the dead-letter list (used when retries are disabled)."""
        self.deadletter(self.__newentry(payload, attempts, error))

    def deadletter(self, entry, member=None):
        """Moves an entry to the capped dead-letter list; when `member` is given it is
        removed from the pending queue in the same transaction."""
        pipe = self.redis.pipeline(transaction=True)
        if member is not None:
            pipe.zrem(self.queuename, member)
        pipe.rpush(self.deadlettername, json.dumps(entry))
        pipe.ltrim(self.deadlettername, -self.deadlettermax, -1)
        length = pipe.execute()[-2]
        if length > self.deadlettermax:
            logging.warning("n8nwebhookretryqueue: dead-letter list is full; dropped %s oldest entries; max=%s list=%s",
                            length - self.deadlettermax, self.deadlettermax, self.deadlettername)
        logging.error("n8nwebhookretryqueue: n8n event could not be delivered and needs operator action; id=%s event=%s attempts=%s error=%s list=%s",
                      entry.get("id"), entry.get("event"), entry.get("attempts"), entry.get("lasterror"), self.deadlettername)

    def backlog(self):
        """Returns (pending entries, dead-lettered entries)."""
        return self.redis.zcard(self.queuename), self.redis.llen(self.deadlettername)

    def __newentry(self, payload, attempts, error, entryid=None):
        return {"id": entryid or str(uuid.uuid4()), "event": payload.get("event"),
                "attempts": attempts, "lasterror": error, "payload": payload}

    def claimdue(self, limit=10, now=None):
        """Leases up to `limit` due entries and returns them as (member, entry)
        pairs. A leased entry stays in Redis: finish it with ack, reschedule or
        deadletter; if the worker dies first it becomes due again when the
        lease expires (at-least-once delivery)."""
        now = time.time() if now is None else now
        members = self._claimscript(keys=[self.queuename], args=[now, limit, now + self.leaseseconds])
        claimed = []
        for member in members:
            try:
                entry = json.loads(member)
            except ValueError:
                self.__deadletterraw(member, "invalid JSON")
                continue
            if isinstance(entry, dict):
                claimed.append((member, entry))
            else:
                self.__deadletterraw(member, "invalid entry")
        return claimed

    def __deadletterraw(self, member, error):
        self.deadletter({"id": None, "event": None, "attempts": None, "lasterror": error, "raw": member}, member)

    def ack(self, member):
        """Removes a leased entry after it was delivered."""
        self.redis.zrem(self.queuename, member)

    def reschedule(self, member, entry, attempts, error):
        """Replaces a leased entry with its next attempt. Returns False when the
        entry was dead-lettered because it reached N8N_WEBHOOK_RETRY_MAX_ATTEMPTS."""
        entry = dict(entry, attempts=attempts, lasterror=error)
        if attempts >= self.maxattempts:
            self.deadletter(entry, member)
            return False
        pipe = self.redis.pipeline(transaction=True)
        pipe.zrem(self.queuename, member)
        pipe.zadd(self.queuename, {json.dumps(entry): time.time() + self.__backoff(attempts)})
        pipe.execute()
        logging.warning("n8nwebhookretryqueue: queued n8n event for retry; id=%s event=%s attempts=%s error=%s",
                        entry.get("id"), entry.get("event"), attempts, error)
        return True

    def __backoff(self, attempts):
        return min(self.backoffseconds * (2 ** (attempts - 1)), self.maxbackoffseconds)
