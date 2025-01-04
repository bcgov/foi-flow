from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json

class FOIOpenInfoAdditionalFiles(db.Model):
    __tablename__ = "FOIOpenInfoAdditionalFiles"
    # Defining the columns
    additionalfileid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer)
    filename = db.Column(db.Text, unique=False, nullable=True)
    s3uripath = db.Column(db.Text, unique=False, nullable=True)
    attributes = db.Column(JSON, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)

    @classmethod
    def create(cls, records):
        db.session.add_all(records)
        db.session.commit()
        _recordids = {}
        for record in records:
            _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.additionalfileid}
        return DefaultMethodResult(True,'Records created', -1, _recordids)
    
    @classmethod
    def fetch(cls, ministryrequestid):
        type_schema = FOIOpenInfoAdditionalFilesSchema(many=True)
        query = db.session.query(FOIOpenInfoAdditionalFiles).filter_by(isactive=True, ministryrequestid=ministryrequestid).all()
        return type_schema.dump(query)
    
    @classmethod
    def delete(cls, additionalfileid, userid):
        record = db.session.query(FOIOpenInfoAdditionalFiles).filter_by(additionalfileid=additionalfileid, isactive=True)
        record.update({FOIOpenInfoAdditionalFiles.isactive: False, FOIOpenInfoAdditionalFiles.updatedby: userid,
                        FOIOpenInfoAdditionalFiles.updated_at: datetime.now().isoformat()}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'OI Additional File updated for id: '+ additionalfileid)
    
    @classmethod
    def bulkdelete(cls, fileids, userid):
        try:
            sql = """update  "FOIOpenInfoAdditionalFiles" 
						set isactive = false, updated_at= now(), updatedby = :userid
                        where additionalfileid in :fileids"""
            rs = db.session.execute(text(sql), {'userid': userid, 'fileids': tuple(fileids)})
            db.session.commit()
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()            
        return DefaultMethodResult(True,'OI Additional File updated for ids: '+ ','.join(str(x) for x in fileids))

class FOIOpenInfoAdditionalFilesSchema(ma.Schema):
    class Meta:
        fields = ("additionalfileid", "ministryrequestid", "filename", "s3uripath", "attributes", "created_at", 
                  "createdby", "updated_at", "updatedby", "isactive")