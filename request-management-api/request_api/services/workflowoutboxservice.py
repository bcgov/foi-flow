import logging
import os
import random
from datetime import datetime, timedelta, timezone

from request_api.models.db import db
from request_api.models.FOIWorkflowEventOutbox import FOIWorkflowEventOutbox, OutboxStatus

"""
Transactional outbox for workflow events destined for n8n.

enqueue()        adds the row to the caller's SQLAlchemy session (inside a savepoint) and,
                 by default, commits it - together with anything the caller still has
                 pending in that session.
dispatch_due()   used by N8NWorkflowOutboxDispatcher. A short transaction claims due rows
                 with FOR UPDATE SKIP LOCKED and pushes nextattemptat to the next backoff
                 time (a lease), then commits; delivery happens outside any transaction.
                 Two dispatchers can therefore never send the same row, and a crash after
                 the claim just means the row is retried when its lease expires.
acknowledge()    n8n reports the outcome. PENDING/DELIVERED -> COMPLETED/FAILED. PENDING is
                 accepted because n8n receiving the event is proof of delivery when the
                 dispatcher died before recording the 2xx. A FAILED row set by the sweeper
                 (lasterror starts with NO_OUTCOME) may still be superseded by the real
                 outcome. Repeating the same acknowledgement is a no-op.
sweepnooutcome() DELIVERED rows with no outcome after a threshold become FAILED/NO_OUTCOME.
replay()         DEAD/FAILED -> PENDING, same event_id (FOI Request Routing dedupes on it).

Retry settings come from N8N_WEBHOOK_RETRY_MAX_ATTEMPTS, _BACKOFF_SECONDS and _MAX_BACKOFF_SECONDS.
"""

NO_OUTCOME_PREFIX = "NO_OUTCOME"
MAXERRORLENGTH = 2000


class AckResult:
    updated = "updated"
    unchanged = "unchanged"
    notfound = "notfound"
    conflict = "conflict"


class workflowoutboxservice:

    def __init__(self):
        self.maxattempts = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS") or 5)
        self.backoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_BACKOFF_SECONDS") or 30)
        self.maxbackoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS") or 3600)
        self.deliverytimeout = float(os.getenv("N8N_WEBHOOK_TIMEOUT_SECONDS") or 10)

    def enqueue(self, payload, commit=True):
        """Stores the event as PENDING. A failure to insert raises after rolling back
        only the savepoint, never the caller's other pending changes."""
        row = FOIWorkflowEventOutbox(
            eventid=payload["event_id"], eventname=payload.get("event"), payload=payload,
            status=OutboxStatus.pending.value, attempts=0, nextattemptat=self.__now(),
        )
        with db.session.begin_nested():
            db.session.add(row)
        if commit:
            db.session.commit()
        return row

    def dispatch_due(self, deliver, batchsize=10, now=None):
        """Claims due rows and delivers each once through deliver(payload) -> n8ndeliveryresult.
        Returns the number of rows that n8n accepted."""
        claimed = self.__claim(batchsize, now)
        delivered = 0
        for eventid, payload, attempts in claimed:
            try:
                result = deliver(payload)
                if self.__recorddelivery(eventid, attempts, result):
                    delivered += 1
            except Exception as ex:
                db.session.rollback()
                logging.exception("workflowoutboxservice: unable to record delivery for event_id=%s; it stays PENDING until its lease expires: %s", eventid, type(ex).__name__)
        return delivered

    def acknowledge(self, eventid, status, error=None, executionid=None, now=None):
        """Returns (AckResult, row)."""
        now = now or self.__now()
        row = FOIWorkflowEventOutbox.getbyeventid(eventid, lock=True)
        if row is None:
            db.session.rollback()
            return AckResult.notfound, None
        if status not in (OutboxStatus.completed.value, OutboxStatus.failed.value):
            db.session.rollback()
            return AckResult.conflict, row
        if status == row.status and not self.__issweepersfailure(row):
            db.session.rollback()
            return AckResult.unchanged, row
        if not self.__canacknowledge(row):
            db.session.rollback()
            logging.warning("workflowoutboxservice: rejected acknowledgement event_id=%s %s -> %s", eventid, row.status, status)
            return AckResult.conflict, row
        row.status = status
        row.lasterror = self.__truncate(error) if status == OutboxStatus.failed.value else None
        row.n8nexecutionid = executionid or row.n8nexecutionid
        row.completedat = now if status == OutboxStatus.completed.value else None
        row.updated_at = now
        db.session.commit()
        logging.info("workflowoutboxservice: event_id=%s acknowledged as %s", eventid, status)
        return AckResult.updated, row

    def sweepnooutcome(self, threshold_minutes, now=None, limit=100):
        """Flags DELIVERED rows older than the threshold. Returns their event ids."""
        now = now or self.__now()
        rows = FOIWorkflowEventOutbox.getstaledelivered(now - timedelta(minutes=threshold_minutes), limit)
        flagged = []
        for row in rows:
            row.status = OutboxStatus.failed.value
            row.lasterror = "%s: no outcome reported by n8n within %s minutes of delivery" % (NO_OUTCOME_PREFIX, threshold_minutes)
            row.updated_at = now
            flagged.append(row.eventid)
        db.session.commit()
        for eventid in flagged:
            logging.warning("workflowoutboxservice: no outcome from n8n; event_id=%s marked FAILED (NO_OUTCOME) and available for replay", eventid)
        return flagged

    def replay(self, eventid, now=None):
        """Returns (AckResult, row): updated = queued again, conflict = not DEAD/FAILED."""
        now = now or self.__now()
        row = FOIWorkflowEventOutbox.getbyeventid(eventid, lock=True)
        if row is None:
            db.session.rollback()
            return AckResult.notfound, None
        if row.status not in (OutboxStatus.dead.value, OutboxStatus.failed.value):
            db.session.rollback()
            return AckResult.conflict, row
        previous = row.status
        row.status = OutboxStatus.pending.value
        row.attempts = 0
        row.nextattemptat = now
        row.replaycount = (row.replaycount or 0) + 1
        row.completedat = None
        row.updated_at = now
        db.session.commit()
        logging.info("workflowoutboxservice: event_id=%s replayed from %s (replaycount=%s)", eventid, previous, row.replaycount)
        return AckResult.updated, row

    def listevents(self, statuses=None, limit=100, offset=0):
        statuses = statuses or [OutboxStatus.dead.value, OutboxStatus.failed.value]
        return [self.todict(row) for row in FOIWorkflowEventOutbox.getbystatuses(statuses, limit, offset)]

    @staticmethod
    def todict(row):
        """Row metadata only - the payload can hold personal information and is not returned."""
        def iso(value):
            return value.isoformat() if value else None
        return {
            "eventid": row.eventid, "event": row.eventname, "status": row.status, "attempts": row.attempts,
            "nextattemptat": iso(row.nextattemptat), "lasterror": row.lasterror,
            "n8nexecutionid": row.n8nexecutionid, "replaycount": row.replaycount,
            "deliveredat": iso(row.deliveredat), "completedat": iso(row.completedat),
            "created_at": iso(row.created_at), "updated_at": iso(row.updated_at),
        }

    def __claim(self, batchsize, now):
        now = now or self.__now()
        claimed = []
        try:
            for row in FOIWorkflowEventOutbox.claimdue(now, batchsize):
                if row.attempts >= self.maxattempts:
                    # attempts are counted at claim time, so this row was claimed max times
                    # without a result being recorded (dispatcher interrupted each time)
                    row.status = OutboxStatus.dead.value
                    row.lasterror = row.lasterror or "Retries exhausted"
                    row.updated_at = now
                    logging.error("workflowoutboxservice: event_id=%s event=%s moved to DEAD (retries exhausted)", row.eventid, row.eventname)
                    continue
                row.attempts += 1
                row.nextattemptat = now + timedelta(seconds=self.__lease(row.attempts))
                row.updated_at = now
                claimed.append((row.eventid, row.payload, row.attempts))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return claimed

    def __recorddelivery(self, eventid, attempts, result):
        now = self.__now()
        row = FOIWorkflowEventOutbox.getbyeventid(eventid, lock=True)
        if row is None or row.status != OutboxStatus.pending.value:
            # acknowledged by n8n (or replayed) while we were sending - nothing to record
            db.session.rollback()
            return result.delivered
        if result.delivered:
            row.status = OutboxStatus.delivered.value
            row.deliveredat = now
            row.lasterror = None
        elif result.retryable and attempts < self.maxattempts:
            row.lasterror = result.error
            logging.warning("workflowoutboxservice: delivery failed, will retry; event_id=%s event=%s attempts=%s error=%s", eventid, row.eventname, attempts, result.error)
        else:
            row.status = OutboxStatus.dead.value
            row.lasterror = result.error
            logging.error("workflowoutboxservice: event moved to DEAD; event_id=%s event=%s attempts=%s error=%s", eventid, row.eventname, attempts, result.error)
        row.updated_at = now
        db.session.commit()
        return result.delivered

    def __canacknowledge(self, row):
        if row.status in (OutboxStatus.pending.value, OutboxStatus.delivered.value):
            return True
        return self.__issweepersfailure(row)

    @staticmethod
    def __issweepersfailure(row):
        return row.status == OutboxStatus.failed.value and (row.lasterror or "").startswith(NO_OUTCOME_PREFIX)

    def __lease(self, attempts):
        backoff = min(self.backoffseconds * (2 ** (attempts - 1)), self.maxbackoffseconds)
        # half the backoff is fixed, the other half random, so retries of
        # events that failed together do not all hit n8n at the same moment
        backoff = backoff / 2 + random.uniform(0, backoff / 2)
        return max(backoff, self.deliverytimeout + 5)

    @staticmethod
    def __truncate(text):
        return text[:MAXERRORLENGTH] if text else text

    @staticmethod
    def __now():
        return datetime.now(timezone.utc)
