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
by the time of their next attempt. Entries that exhaust
N8N_WEBHOOK_RETRY_MAX_ATTEMPTS, fail with a non-retryable error, or fail
while N8N_WEBHOOK_RETRY_ENABLED is false move to the "<queue>:failed" list,
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
        self.redis = redisclient or redis.Redis(
            host=os.getenv("EVENT_QUEUE_HOST") or "localhost",
            port=int(os.getenv("EVENT_QUEUE_PORT") or 6379),
            password=os.getenv("EVENT_QUEUE_PASSWORD") or None,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
        )

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
        """Removes and returns up to `limit` entries whose next attempt is due."""
        now = time.time() if now is None else now
        claimed = []
        for member in self.redis.zrangebyscore(self.queuename, "-inf", now, start=0, num=limit):
            if self.redis.zrem(self.queuename, member):
                claimed.append(json.loads(member))
        return claimed

    def __backoff(self, attempts):
        return min(self.backoffseconds * (2 ** (attempts - 1)), self.maxbackoffseconds)
