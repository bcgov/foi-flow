from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey

from .db import db, ma


class DocumentTemplate(db.Model):
    __tablename__ = 'DocumentTemplates'
    # Defining the columns

    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_type_id = db.Column(db.Integer, ForeignKey('DocumentTypes.document_type_id'), nullable=False)
    cdogs_hash_code = db.Column(db.String(64), nullable=True, unique=True)
    extension = db.Column(db.String(10), nullable=False)

    @classmethod
    def get_template_by_type(cls, document_type_id: int, extension: str = "docx"):
        """Given a type and optionally an extension, return the template."""

        query = cls.query.filter_by(document_type_id = document_type_id). \
            filter(DocumentTemplate.extension == extension)

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


class DocumentTemplateSchema(ma.Schema):
    class Meta:
        model = DocumentTemplate
        exclude = []
