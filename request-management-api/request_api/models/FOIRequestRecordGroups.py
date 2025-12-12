
from .db import db


class FOIRequestRecordGroups(db.Model):
    """
    Association table: many FOIRequestRecord <-> many FOIRequestRecordGroup
    """
    __tablename__ = "FOIRequestRecordGroups"

    document_set_id = db.Column(
        db.Integer,
        db.ForeignKey("FOIRequestRecordGroup.document_set_id", ondelete="CASCADE"),
        primary_key=True
    )

    record_id = db.Column(
        db.Integer,
        db.ForeignKey("FOIRequestRecords.recordid", ondelete="CASCADE"),
        primary_key=True
    )

    def __repr__(self) -> str:
        return f"<FOIRequestRecordGroups(set={self.document_set_id}, record={self.record_id})>"

    @classmethod
    def remove_records(cls, document_set_id: int, record_ids: set[int]) -> None:
        if not record_ids:
            return

        (
            db.session.query(cls)
            .filter(
                cls.document_set_id == document_set_id,
                cls.record_id.in_(record_ids),
            )
            .delete(synchronize_session=False)
        )

    @classmethod
    def get_record_ids(cls, document_set_id: int) -> set[int]:
        rows = (
            db.session.query(cls.record_id)
            .filter(cls.document_set_id == document_set_id)
            .all()
        )
        return {r[0] for r in rows}

    @classmethod
    def add_records(cls, document_set_id: int, record_ids: set[int]) -> None:
        if not record_ids:
            return

        rows = [{"document_set_id": document_set_id, "record_id": rid}
                for rid in record_ids]

        db.session.execute(cls.__table__.insert(), rows)

    @classmethod
    def get_groups_for_record(cls, record_id: int) -> list[int]:
        return (
            db.session.query(FOIRequestRecordGroups.document_set_id)
            .filter(FOIRequestRecordGroups.record_id == record_id)
            .order_by(FOIRequestRecordGroups.document_set_id)
            .scalars()
            .all()
        )

    @classmethod
    def remove_from_other_groups(cls, document_set_id: int, record_ids: set[int]) -> None:
        if not record_ids:
            return

        (
            db.session.query(cls)
            .filter(
                cls.record_id.in_(record_ids),
                cls.document_set_id != document_set_id,
            )
            .delete(synchronize_session=False)
        )


