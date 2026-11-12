from enum import Enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from .db import db


class OutboxStatus(Enum):
    """PENDING   - waiting to be (re)sent to n8n
    DELIVERED - n8n accepted the event (2xx); outcome not reported yet
    COMPLETED - n8n reported the run finished
    FAILED    - n8n reported a failed run, or no outcome arrived in time (see lasterror)
    DEAD      - never reached n8n: retries exhausted or a non-retryable HTTP error"""
    pending = "PENDING"
    delivered = "DELIVERED"
    completed = "COMPLETED"
    failed = "FAILED"
    dead = "DEAD"


class OrderScope:
    """What a state event is ordered by: intake events by raw request, ministry-level events by ministry request.
    A ministry event also carries its raw request id, so it counts for the raw request too."""
    rawrequest = "raw_request_id"
    ministryrequest = "ministry_request_id"
    all = (rawrequest, ministryrequest)


class FOIWorkflowEventOutbox(db.Model):
    """Transactional outbox of workflow events destined for n8n.

    All timestamps are naive UTC. Rows are only inserted/claimed/updated through
    workflowoutboxservice; this class holds the table definition and queries."""
    __tablename__ = 'FOIWorkflowEventOutbox'

    outboxid = db.Column(db.BigInteger().with_variant(db.Integer, 'sqlite'), primary_key=True, autoincrement=True)
    eventid = db.Column(db.String(36), nullable=False, unique=True)
    eventname = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON().with_variant(JSONB, 'postgresql'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=OutboxStatus.pending.value)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    nextattemptat = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    lasterror = db.Column(db.Text, nullable=True)
    n8nexecutionid = db.Column(db.String(100), nullable=True)
    replaycount = db.Column(db.Integer, nullable=False, default=0)
    deliveredat = db.Column(db.DateTime, nullable=True)
    completedat = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # set by n8n FOI Request Routing when it claims the event (workflowoutboxservice.claim)
    claimedat = db.Column(db.DateTime, nullable=True)
    rawrequestid = db.Column(db.String(50), nullable=True)
    foirequestid = db.Column(db.String(50), nullable=True)
    ministryrequestid = db.Column(db.String(50), nullable=True)
    requeststatus = db.Column(db.String(100), nullable=True)
    # occurred_at of a state event once it was allowed to run: the newest value per request is the ordering
    # watermark (an older state event arriving later is stale). Never set for action events.
    stateoccurredat = db.Column(db.DateTime, nullable=True)
    # set by the retention job once the personal data in payload has been removed
    payloadscrubbedat = db.Column(db.DateTime, nullable=True)

    @classmethod
    def getbyexecutionid(cls, executionid):
        return db.session.query(FOIWorkflowEventOutbox).filter(
            FOIWorkflowEventOutbox.n8nexecutionid == executionid,
        ).order_by(FOIWorkflowEventOutbox.outboxid.desc()).first()

    @classmethod
    def neweststateoccurredat(cls, scope, scopekey, excepteventid):
        """The newest state event already allowed to run for the request, ignoring the event itself."""
        column = FOIWorkflowEventOutbox.rawrequestid if scope == OrderScope.rawrequest else FOIWorkflowEventOutbox.ministryrequestid
        return db.session.query(db.func.max(FOIWorkflowEventOutbox.stateoccurredat)).filter(
            column == scopekey,
            FOIWorkflowEventOutbox.eventid != excepteventid,
        ).scalar()

    @classmethod
    def getscrubbable(cls, cutoff, limit):
        """COMPLETED rows older than the cutoff whose payload still holds the event."""
        return db.session.query(FOIWorkflowEventOutbox).filter(
            FOIWorkflowEventOutbox.status == OutboxStatus.completed.value,
            FOIWorkflowEventOutbox.payloadscrubbedat.is_(None),
            FOIWorkflowEventOutbox.completedat < cutoff,
        ).order_by(FOIWorkflowEventOutbox.outboxid).limit(limit).with_for_update(skip_locked=True).all()

    @classmethod
    def deletecompletedbefore(cls, cutoff, limit):
        """Deletes up to `limit` COMPLETED rows completed before the cutoff. Returns the number deleted."""
        ids = [row.outboxid for row in db.session.query(FOIWorkflowEventOutbox.outboxid).filter(
            FOIWorkflowEventOutbox.status == OutboxStatus.completed.value,
            FOIWorkflowEventOutbox.completedat < cutoff,
        ).order_by(FOIWorkflowEventOutbox.outboxid).limit(limit).all()]
        if ids:
            db.session.query(FOIWorkflowEventOutbox).filter(
                FOIWorkflowEventOutbox.outboxid.in_(ids)).delete(synchronize_session=False)
        return len(ids)

    @classmethod
    def getbyeventid(cls, eventid, lock=False):
        query = db.session.query(FOIWorkflowEventOutbox).filter(FOIWorkflowEventOutbox.eventid == eventid)
        if lock:
            query = query.with_for_update()
        return query.first()

    @classmethod
    def claimdue(cls, now, limit):
        """PENDING rows whose next attempt is due, locked FOR UPDATE SKIP LOCKED so a
        concurrent dispatcher (another pod/worker) skips rows this transaction holds."""
        return db.session.query(FOIWorkflowEventOutbox).filter(
            FOIWorkflowEventOutbox.status == OutboxStatus.pending.value,
            FOIWorkflowEventOutbox.nextattemptat <= now,
        ).order_by(FOIWorkflowEventOutbox.outboxid).limit(limit).with_for_update(skip_locked=True).all()

    @classmethod
    def getstaledelivered(cls, cutoff, limit):
        return db.session.query(FOIWorkflowEventOutbox).filter(
            FOIWorkflowEventOutbox.status == OutboxStatus.delivered.value,
            FOIWorkflowEventOutbox.deliveredat <= cutoff,
        ).order_by(FOIWorkflowEventOutbox.outboxid).limit(limit).with_for_update(skip_locked=True).all()

    @classmethod
    def getbystatuses(cls, statuses, limit, offset=0):
        return db.session.query(FOIWorkflowEventOutbox).filter(
            FOIWorkflowEventOutbox.status.in_(statuses),
        ).order_by(FOIWorkflowEventOutbox.outboxid.desc()).limit(limit).offset(offset).all()
