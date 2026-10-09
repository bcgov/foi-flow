from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB, insert as pg_insert

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
    def _build_upsert_statement(cls, userid, preferences, schema_version):
        # A single PostgreSQL statement avoids a race when two sessions
        # create a user's first preference document concurrently.
        now = datetime.now()
        insert_statement = pg_insert(cls.__table__).values(
            userid=userid,
            preferences=preferences,
            schema_version=schema_version,
            created_at=now
        )

        return insert_statement.on_conflict_do_update(
            index_elements=[cls.__table__.c.userid],
            set_={
                "preferences": insert_statement.excluded.preferences,
                "schema_version": insert_statement.excluded.schema_version,
                "updated_at": now
            }
        )

    @classmethod
    def upsert(cls, userid, preferences, schema_version):
        try:
            statement = cls._build_upsert_statement(
                userid, preferences, schema_version
            )
            db.session.execute(statement)
            db.session.commit()

            return cls.getbyuserid(userid)

        except Exception:
            db.session.rollback()
            raise

    def asdict(self):
        return {
            "schemaVersion": self.schema_version,
            "preferences": self.preferences or {}
        }
