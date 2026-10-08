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
