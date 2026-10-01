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
by the time of their next attempt; claimdue() removes an entry with ZREM
before it is re-sent, so only one API pod/worker ever claims a given entry.
Entries that exhaust N8N_WEBHOOK_RETRY_MAX_ATTEMPTS, or fail with a
non-retryable error, move to the "<queue>:failed" list for operator review.

Uses the EVENT_QUEUE_* Redis connection already configured for this API.
"""

class n8nwebhookretryqueue:

    def __init__(self, redisclient=None):
        self.queuename = os.getenv("N8N_WEBHOOK_RETRY_QUEUE") or "foi-n8n-webhook-retry"
        self.deadlettername = self.queuename + ":failed"
        self.maxattempts = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS") or 5)
        self.backoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_BACKOFF_SECONDS") or 30)
        self.maxbackoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS") or 3600)
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
        entry = {"id": entryid or str(uuid.uuid4()), "event": payload.get("event"),
                 "attempts": attempts, "lasterror": error, "payload": payload}
        if attempts >= self.maxattempts:
            self.deadletter(entry)
            return False
        nextattemptat = time.time() + self.__backoff(attempts)
        self.redis.zadd(self.queuename, {json.dumps(entry): nextattemptat})
        logging.warning("n8nwebhookretryqueue: queued n8n event for retry; id=%s event=%s attempts=%s error=%s",
                        entry["id"], entry["event"], attempts, error)
        return True

    def claimdue(self, limit=10, now=None):
        """Removes and returns up to `limit` entries whose next attempt is due."""
        now = time.time() if now is None else now
        claimed = []
        for member in self.redis.zrangebyscore(self.queuename, "-inf", now, start=0, num=limit):
            if self.redis.zrem(self.queuename, member):
                claimed.append(json.loads(member))
        return claimed

    def deadletter(self, entry):
        self.redis.rpush(self.deadlettername, json.dumps(entry))
        logging.error("n8nwebhookretryqueue: n8n event could not be delivered and needs operator action; id=%s event=%s attempts=%s error=%s list=%s",
                      entry.get("id"), entry.get("event"), entry.get("attempts"), entry.get("lasterror"), self.deadlettername)

    def __backoff(self, attempts):
        return min(self.backoffseconds * (2 ** (attempts - 1)), self.maxbackoffseconds)
