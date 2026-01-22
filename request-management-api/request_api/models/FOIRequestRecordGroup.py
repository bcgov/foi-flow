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
    request_id = Column(Integer, nullable=False, index=True)

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
        Index(
            "ix_fr_group_request",
            "ministry_request_id",
        ),
    )

    def __repr__(self):
        return (
            f"<FOIRequestRecordGroup(document_set_id={self.document_set_id}, "
            f"ministry_request_id={self.ministry_request_id}, "
            f"request_id={self.request_id}, "
            f"name={self.name!r}, "
            f"is_active={self.is_active})>"
        )

    @classmethod
    def create_group(
            cls,
            ministry_request_id: int,
            request_id: int,
            name: str,
            created_by: str,
            records: List[int],
    ) -> "FOIRequestRecordGroup | None":

        try:
            # 1. Insert parent group
            group = cls(
                ministry_request_id=ministry_request_id,
                request_id=request_id,
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

    @classmethod
    def get_by_ministry_request_id(
            cls, ministry_request_id: int, include_records: bool = False
    ) -> list["FOIRequestRecordGroup"]:
        """
        Retrieve all active FOIRequestRecordGroup rows for a given ministry_request_id.
        Optionally loads the associated records using selectinload.
        """

        query = db.session.query(cls).filter(
            cls.ministry_request_id == ministry_request_id,
            cls.is_active.is_(True)
        )

        if include_records:
            query = query.options(db.selectinload(cls.records))

        return query.order_by(cls.document_set_id.asc()).all()


    @classmethod
    def get_active_groups_for_request(
            cls,
            ministry_request_id: int,
            request_id: int,
            document_set_id: int | None = None,
            include_records: bool = False,
    ) -> list["FOIRequestRecordGroup"]:
        """
        Retrieve active document groups for a ministry + request.
        Optionally filter by document_set_id.
        """
        query = (
            db.session.query(cls)
            .filter(
                cls.ministry_request_id == ministry_request_id,
                cls.request_id == request_id,
                cls.is_active.is_(True),
            )
        )

        if document_set_id:
            query = query.filter(cls.document_set_id == document_set_id)

        if include_records:
            query = query.options(db.selectinload(cls.records))

        return query.order_by(cls.document_set_id.asc()).all()

    @classmethod
    def find_record_association(
            cls,
            *,
            ministry_request_id: int,
            request_id: int,
            document_set_id: int,
            record_id: int,
    ):
        """
        Validate that a record belongs to an active document set
        within the given ministry + request scope.
        """
        return (
            db.session.query(cls)
            .join(FOIRequestRecordGroups, cls.document_set_id == FOIRequestRecordGroups.document_set_id)
            .filter(
                cls.ministry_request_id == ministry_request_id,
                cls.request_id == request_id,
                cls.document_set_id == document_set_id,
                cls.is_active.is_(True),
                FOIRequestRecordGroups.record_id == record_id,
            )
            .first()
        )

