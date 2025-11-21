from sqlalchemy import JSON
from request_api.models import db


class FOIRequestRecordHistory(db.Model):
    __tablename__ = 'FOIRequestRecordHistory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Link back to the current record
    recordid = db.Column(
        db.Integer,
        db.ForeignKey('FOIRequestRecords.recordid'),
        nullable=False,
    )

    # Old version number from the original table
    version = db.Column(db.Integer, nullable=False)

    foirequestid = db.Column(db.Integer, nullable=False)
    ministryrequestid = db.Column(db.Integer, nullable=True)
    ministryrequestversion = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.Text, nullable=True)
    s3uripath = db.Column(db.Text, nullable=True)
    attributes = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), nullable=True)
    isactive = db.Column(db.Boolean, nullable=False, default=True)
    replacementof = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('recordid', 'version', name='uq_foirecordhist_recordid_version'),
    )

