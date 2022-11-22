from .db import  db, ma
from .default_method_result import DefaultMethodResult
from datetime import datetime
from request_api.utils.enums import DocumentPathMapperCategory
import json
from sqlalchemy import func

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
    def getdocumentpath(cls, category, programarea=None):
        documentpath_schema = DocumentPathMapperSchema()
        query = db.session.query(DocumentPathMapper).filter(DocumentPathMapper.isactive == True, func.lower(DocumentPathMapper.category) == category.lower())
        if category.lower() == DocumentPathMapperCategory.Records.value.lower():
            query = query.filter(DocumentPathMapper.bucket.ilike(programarea.lower() + '%'))
        pathmap = documentpath_schema.dump(query.first())
        pathmap['attributes'] = json.loads(pathmap['attributes'])
        return pathmap


class DocumentPathMapperSchema(ma.Schema):
    class Meta:
        fields = ('documentpathid', 'category', 'bucket','attributes')