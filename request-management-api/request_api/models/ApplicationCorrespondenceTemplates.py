from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey

from .db import db, ma


class ApplicationCorrespondenceTemplate(db.Model):
    __tablename__ = 'ApplicantCorrespondenceTemplates'
    # Defining the columns

    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documenturipath = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    name = db.Column(db.String(500), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def get_template_by_id(cls, template_id: int):
        """Given a type and optionally an extension, return the template."""

        query = cls.query.filter_by(template_id = template_id). \
            filter(ApplicationCorrespondenceTemplate.template_id == template_id)

        return query.one_or_none()

    @classmethod
    def getapplicantcorrespondencetemplates(cls):
        correspondencetemplate_schema = ApplicationCorrespondenceTemplateSchema(many=True)
        query = db.session.query(ApplicationCorrespondenceTemplate).filter_by(active=True).all()
        return correspondencetemplate_schema.dump(query)    

    @staticmethod
    def commit():
        """Commit the session."""
        db.session.commit()

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self


class ApplicationCorrespondenceTemplateSchema(ma.Schema):
    class Meta:
        model = ApplicationCorrespondenceTemplate
        exclude = []
