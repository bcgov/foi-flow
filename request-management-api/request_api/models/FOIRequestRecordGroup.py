from typing import List

from flask import current_app
from sqlalchemy import Column, Integer, String, TIMESTAMP, Index
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import db
from .FOIRequestRecordGroups import FOIRequestRecordGroups


class FOIRequestRecordGroup(db.Model):
    __tablename__ = 'FOIRequestRecordGroup'

    document_set_id = Column(Integer, primary_key=True, autoincrement=True)
    ministry_request_id = Column(Integer, nullable=False, index=True)

    name = Column(String(255))
    is_active = db.Column(db.Boolean, unique=False, nullable=False, default=True)

    created_by = Column(String(120))
    created_at = Column(TIMESTAMP, server_default=func.now())

    updated_at = db.Column(db.DateTime, nullable=True)
    updated_by = db.Column(db.String(120), unique=False, nullable=True)

    # Many-to-many: group -> records
    records = relationship(
        "FOIRequestRecord",
        secondary="FOIRequestRecordGroups",
        back_populates="groups",
        lazy="selectin"
    )

    __table_args__ = (
        # old composite index included ministryrequestversion; now just mrid or drop entirely
        Index(
            "ix_fr_group_request",
            "ministry_request_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<FOIRequestRecordGroup(documentsetid={self.documentsetid}, "
            f"mrid={self.ministryrequestid}, "
            f"name={self.name!r}, isactive={self.isactive})>"
        )

    @classmethod
    def create_group(
            cls,
            ministry_request_id: int,
            name: str,
            created_by: str,
            records: List[int],
    ) -> "FOIRequestRecordGroup | None":

        try:
            # 1. Insert parent group
            group = cls(
                ministry_request_id=ministry_request_id,
                name=name,
                created_by=created_by,
            )
            db.session.add(group)
            db.session.flush()  # now group.document_set_id is available

            # 2. Insert into association table
            for rid in sorted(set(records)):
                db.session.execute(
                    db.insert(FOIRequestRecordGroups).values(
                        document_set_id=group.document_set_id,
                        record_id=rid,
                    )
                )

            db.session.commit()
            return group

        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Database error creating FOIRequestRecordGroup")
            return None


    @classmethod
    def get_by_name(cls, ministry_request_id: int, name: str) -> "FOIRequestRecordGroup | None":
        return (
            db.session.query(cls)
            .filter(
                cls.ministry_request_id == ministry_request_id,
                func.lower(cls.name) == func.lower(name),
                cls.is_active.is_(True)
            )
            .first()
        )

    @classmethod
    def exists_with_name(cls, ministry_request_id: int, name: str) -> bool:
        return (
            db.session.query(cls)
            .filter(
                cls.ministry_request_id == ministry_request_id,
                func.lower(cls.name) == func.lower(name),  # case-insensitive
                cls.is_active.is_(True)
            )
            .first()
            is not None
        )