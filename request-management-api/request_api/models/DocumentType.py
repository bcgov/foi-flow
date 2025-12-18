from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey

from .db import db, ma


class DocumentType(db.Model):
    __tablename__ = 'DocumentTypes'
    # Defining the columns

    document_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_type_name = db.Column(db.String(30), nullable=False, unique=False)
    description = db.Column(db.String(100), unique=False, nullable=True)

    @classmethod
    def get_document_type_by_name(cls, document_type_name: str):
        """Given a type and optionally an extension, return the template."""

        query = cls.query.filter_by(document_type_name = document_type_name)

        return query.one_or_none()

    @staticmethod
    def commit():
        """Commit the session."""
        db.session.commit()

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self


class DocumentTypeSchema(ma.Schema):
    class Meta:
        model = DocumentType
        exclude = []
