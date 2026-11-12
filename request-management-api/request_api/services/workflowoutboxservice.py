import logging
import os
import random
import re
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session

from request_api.models.db import db
from request_api.models.FOIWorkflowEventOutbox import FOIWorkflowEventOutbox, OrderScope, OutboxStatus

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
recordenqueuefailure()
                 last resort when enqueue() keeps failing: writes a DEAD row (lasterror starts
                 with ENQUEUE_FAILED) in a separate session so the event can be found and replayed.
claim()          called by n8n FOI Request Routing before it processes an event. In ONE transaction
                 it answers proceed / duplicate / in_progress / stale: duplicate = the event already
                 COMPLETED; in_progress = another execution holds a live claim (lease); stale = an
                 older state event than one already allowed to run for the request (the newest
                 stateoccurredat on the outbox rows of that request is the ordering watermark).
                 This replaces the idempotency, ordering and execution lookups n8n used to do against
                 the foi-process-audit Data Table. acknowledge() and replay() release the claim.
findbyexecution()
                 maps a failed n8n execution id to its event (the claim recorded it), for the error handler.
scrubpayloads() / purgecompleted()
                 retention: remove the personal data from old COMPLETED payloads, then delete old rows.

Retry settings come from N8N_WEBHOOK_RETRY_MAX_ATTEMPTS, _BACKOFF_SECONDS and _MAX_BACKOFF_SECONDS.
The claim lease comes from N8N_OUTBOX_CLAIM_LEASE_MINUTES (default N8N_OUTBOX_NO_OUTCOME_MINUTES, 30).
"""

NO_OUTCOME_PREFIX = "NO_OUTCOME"
ENQUEUE_FAILED_PREFIX = "ENQUEUE_FAILED"
MAXERRORLENGTH = 2000
OCCURRED_AT_FORMAT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00$")


class AckResult:
    updated = "updated"
    unchanged = "unchanged"
    notfound = "notfound"
    conflict = "conflict"


class ClaimDecision:
    proceed = "proceed"
    duplicate = "duplicate"
    inprogress = "in_progress"
    stale = "stale"


class EventKind:
    """state events change the request and are order-checked; action events are always processed."""
    state = "state"
    action = "action"
    all = (state, action)


class workflowoutboxservice:

    def __init__(self):
        self.maxattempts = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_ATTEMPTS") or 5)
        self.backoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_BACKOFF_SECONDS") or 30)
        self.maxbackoffseconds = int(os.getenv("N8N_WEBHOOK_RETRY_MAX_BACKOFF_SECONDS") or 3600)
        self.deliverytimeout = float(os.getenv("N8N_WEBHOOK_TIMEOUT_SECONDS") or 10)
        self.claimleaseminutes = int(os.getenv("N8N_OUTBOX_CLAIM_LEASE_MINUTES") or os.getenv("N8N_OUTBOX_NO_OUTCOME_MINUTES") or 30)

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

    @staticmethod
    def recoversession():
        """Rolls the caller's session back only if a failed commit left it unusable, so a
        retry of enqueue() can run. A healthy session (failed insert rolled back to its
        savepoint) keeps the caller's pending changes."""
        if not db.session.is_active:
            db.session.rollback()

    def recordenqueuefailure(self, payload, error):
        """Writes a DEAD row for an event that could not be enqueued, in its own session so a
        broken caller session cannot block it. Falls back to a row without the payload body if
        the full payload cannot be stored. Returns True if a row was written; False if the
        database is unreachable (the caller must then rely on its log line)."""
        message = self.__truncate("%s: %s" % (ENQUEUE_FAILED_PREFIX, error))
        minimal = {key: payload.get(key) for key in ("event", "event_id", "occurred_at")}
        for stored, note in ((payload, message), (minimal, self.__truncate(message + " (payload not stored)"))):
            session = Session(bind=db.engine)
            try:
                now = self.__now()
                session.add(FOIWorkflowEventOutbox(
                    eventid=payload["event_id"], eventname=payload.get("event") or "unknown", payload=stored,
                    status=OutboxStatus.dead.value, attempts=0, nextattemptat=now, lasterror=note,
                    created_at=now, updated_at=now,
                ))
                session.commit()
                return True
            except Exception as ex:
                session.rollback()
                logging.exception("workflowoutboxservice: unable to record the enqueue failure for event_id=%s (payload stored=%s): %s", payload.get("event_id"), stored is payload, type(ex).__name__)
            finally:
                session.close()
        return False

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
        row.claimedat = None  # the run is over, a replay must not be blocked by its lease
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
        row.claimedat = None
        row.updated_at = now
        db.session.commit()
        logging.info("workflowoutboxservice: event_id=%s replayed from %s (replaycount=%s)", eventid, previous, row.replaycount)
        return AckResult.updated, row

    def claim(self, eventid, executionid, kind=EventKind.action, scope=None, scopekey=None, occurredat=None,
              requestids=None, now=None):
        """Decides, in one transaction, whether the n8n execution `executionid` may process the event.
        Returns a ClaimDecision. Raises ValueError for input the caller got wrong.

        kind=state with scope/scopekey/occurredat is order-checked: it is stale when another event of the
        same request, with a newer occurred_at, was already allowed to run (an equal timestamp runs, so a
        replay of the same event works). The ordering state is the `stateoccurredat` of the outbox rows
        themselves: a ministry event records its raw request id too, so a late intake event for that raw
        request becomes stale. Claims for one request are serialised (Postgres advisory lock) so two events
        cannot pass the check together. An event without an outbox row (sent by hand) is still
        order-checked but not claimed."""
        if kind not in EventKind.all:
            raise ValueError("kind must be one of %s" % ", ".join(EventKind.all))
        moment = self.__orderingmoment(kind, scope, scopekey, occurredat)
        now = self.__naive(now or self.__now())
        try:
            row = FOIWorkflowEventOutbox.getbyeventid(eventid, lock=True)
            decision = self.__existingclaimdecision(row, executionid, now)
            if decision is None:
                requestids = self.__claimrequestids(requestids, scope, scopekey, moment)
                if moment is not None and self.__isstale(eventid, scope, scopekey, moment, requestids):
                    decision = ClaimDecision.stale
            if decision is not None:
                db.session.rollback()
                return decision
            if row is not None:
                self.__recordclaim(row, executionid, requestids, moment, now)
            db.session.commit()
            return ClaimDecision.proceed
        except Exception:
            db.session.rollback()
            raise

    def __orderingmoment(self, kind, scope, scopekey, occurredat):
        """The parsed occurred_at when the event is order-checked, else None. Raises ValueError for a bad scope or timestamp."""
        if kind != EventKind.state or not (occurredat and scope and scopekey):
            return None
        if scope not in OrderScope.all:
            raise ValueError("scope must be one of %s" % ", ".join(OrderScope.all))
        return self.__parsemoment(occurredat)

    def __existingclaimdecision(self, row, executionid, now):
        """duplicate or in_progress when the event's outbox row says so, else None (no row, or free to run)."""
        if row is None:
            return None
        if row.status == OutboxStatus.completed.value:
            return ClaimDecision.duplicate
        if self.__claimislive(row, executionid, now):
            return ClaimDecision.inprogress
        return None

    @staticmethod
    def __claimrequestids(requestids, scope, scopekey, moment):
        """A copy of the request ids; for an order-checked event its own scope key is always one of them."""
        requestids = dict(requestids or {})
        if moment is not None:
            requestids["rawrequestid" if scope == OrderScope.rawrequest else "ministryrequestid"] = scopekey
        return requestids

    def __isstale(self, eventid, scope, scopekey, moment, requestids):
        """True when another event of the same request with a newer occurred_at was already allowed to run.
        Takes the per-request advisory lock first, so the check and the recording of this claim are atomic."""
        self.__lockrequests(requestids)
        newest = FOIWorkflowEventOutbox.neweststateoccurredat(scope, str(scopekey), eventid)
        return newest is not None and newest > moment

    def __recordclaim(self, row, executionid, requestids, moment, now):
        row.claimedat = now
        row.n8nexecutionid = str(executionid)[:100] if executionid else row.n8nexecutionid
        self.__recordrequestids(row, requestids)
        if moment is not None:
            row.stateoccurredat = moment
        row.updated_at = now

    def findbyexecution(self, executionid):
        """The event an n8n execution claimed, as a dict, or None. Never returns the payload."""
        row = FOIWorkflowEventOutbox.getbyexecutionid(str(executionid))
        if row is None:
            return None
        return {"event_id": row.eventid, "event": row.eventname, "raw_request_id": row.rawrequestid,
                "foi_request_id": row.foirequestid, "ministry_request_id": row.ministryrequestid,
                "status": row.requeststatus, "outbox_status": row.status}

    def scrubpayloads(self, days, batchsize=1000, now=None):
        """Removes the event (personal data) from COMPLETED rows completed more than `days` days ago,
        keeping eventid, name, status and timestamps. Returns the number of rows scrubbed."""
        now = self.__naive(now or self.__now())
        try:
            rows = FOIWorkflowEventOutbox.getscrubbable(now - timedelta(days=days), batchsize)
            for row in rows:
                row.payload = {"event_id": row.eventid, "event": row.eventname, "scrubbed": True}
                row.payloadscrubbedat = now
                row.updated_at = now
            db.session.commit()
            return len(rows)
        except Exception:
            db.session.rollback()
            raise

    def purgecompleted(self, days, batchsize=1000, now=None):
        """Deletes COMPLETED rows completed more than `days` days ago. The duplicate check and the ordering
        check read these rows, so `days` must be far longer than an event can still be redelivered or
        replayed (DEAD and FAILED rows, the ones that can be replayed, are never deleted).
        Returns the number of rows deleted."""
        now = self.__naive(now or self.__now())
        cutoff = now - timedelta(days=days)
        try:
            deleted = FOIWorkflowEventOutbox.deletecompletedbefore(cutoff, batchsize)
            db.session.commit()
            return deleted
        except Exception:
            db.session.rollback()
            raise

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
            "claimedat": iso(row.claimedat), "rawrequestid": row.rawrequestid,
            "foirequestid": row.foirequestid, "ministryrequestid": row.ministryrequestid,
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

    def __claimislive(self, row, executionid, now):
        """Another execution claimed the event less than a lease ago. The same execution may claim again."""
        if row.claimedat is None or (row.n8nexecutionid or "") == (str(executionid) if executionid else ""):
            return False
        return row.claimedat > now - timedelta(minutes=self.claimleaseminutes)

    @staticmethod
    def __lockrequests(requestids):
        """Serialises the claims of one request: a transaction-scoped Postgres advisory lock on the raw and
        the ministry request id (always in that order, so two claims cannot deadlock). The lock is released
        at commit or rollback; the next claim then sees the previous one's stateoccurredat. Other databases
        (the SQLite of the unit tests) have a single writer and need no lock."""
        if db.session.get_bind().dialect.name != "postgresql":
            return
        for label, key in (("raw", requestids.get("rawrequestid")), ("ministry", requestids.get("ministryrequestid"))):
            if key not in (None, ""):
                db.session.execute(text("SELECT pg_advisory_xact_lock(hashtext(:key))"), {"key": "foiworkflow:%s:%s" % (label, key)})

    @staticmethod
    def __parsemoment(occurredat):
        if not isinstance(occurredat, str) or not OCCURRED_AT_FORMAT.match(occurredat):
            raise ValueError("occurred_at must be a UTC ISO-8601 timestamp with microseconds")
        return datetime.strptime(occurredat[:-6], "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def __recordrequestids(row, requestids):
        def text(key, length):
            value = requestids.get(key)
            return str(value)[:length] if value not in (None, "") else None
        row.rawrequestid = text("rawrequestid", 50) or row.rawrequestid
        row.foirequestid = text("foirequestid", 50) or row.foirequestid
        row.ministryrequestid = text("ministryrequestid", 50) or row.ministryrequestid
        row.requeststatus = text("status", 100) or row.requeststatus

    @staticmethod
    def __naive(moment):
        """The columns hold naive UTC."""
        if moment.tzinfo is not None:
            return moment.astimezone(timezone.utc).replace(tzinfo=None)
        return moment

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
