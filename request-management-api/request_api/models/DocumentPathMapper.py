from .db import  db, ma
from .default_method_result import DefaultMethodResult
from datetime import datetime

class DocumentPathMapper(db.Model):
    __tablename__ = 'DocumentPathMapper' 
    # Defining the columns
    documentpathid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    category = db.Column(db.Text, unique=False, nullable=False)
    bucket = db.Column(db.Text, unique=False, nullable=False)
    attributes = db.Column(db.Text, unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, default='System')
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def getdocumentpath(cls):
        documentpath_schema = DocumentPathMapperSchema(many=True)
        query = db.session.query(DocumentPathMapper).filter_by(isactive=True).all()
        return documentpath_schema.dump(query)


class DocumentPathMapperSchema(ma.Schema):
    class Meta:
        fields = ('documentpathid', 'category', 'bucket','attributes')