from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from .db import db


class FOIUserPreference(db.Model):
    """Server-backed application preferences for an authenticated FOI MOD user."""

    __tablename__ = "FOIUserPreferences"

    userpreferenceid = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    # Deliberately uses the normalized authenticated user id returned by
    # AuthHelper.getuserid() rather than depending on the FOIUsers sync table.
    userid = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    preferences = db.Column(
        JSONB,
        nullable=False,
        default=dict
    )

    schema_version = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=True
    )

    @classmethod
    def getbyuserid(cls, userid):
        return (
            db.session
            .query(cls)
            .filter_by(userid=userid)
            .one_or_none()
        )

    @classmethod
    def upsert(cls, userid, preferences, schema_version):
        try:
            preference = cls.getbyuserid(userid)

            if preference is None:
                preference = cls(
                    userid=userid,
                    preferences=preferences,
                    schema_version=schema_version
                )
                db.session.add(preference)
            else:
                preference.preferences = preferences
                preference.schema_version = schema_version
                preference.updated_at = datetime.now()

            db.session.commit()

            return preference

        except Exception:
            db.session.rollback()
            raise

    def asdict(self):
        return {
            "schemaVersion": self.schema_version,
            "preferences": self.preferences or {}
        }
