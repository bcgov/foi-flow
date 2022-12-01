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
class FOIRequestRecord(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestRecords' 
    # Defining the columns
    recordid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version =db.Column(db.Integer,primary_key=True,nullable=False)
    foirequestid =db.Column(db.Integer,  nullable=False)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    filename = db.Column(db.Text, unique=False, nullable=True)
    s3uripath = db.Column(db.Text, unique=False, nullable=True)
    attributes = db.Column(JSON, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

 
    @classmethod
    def create(cls, records):
        db.session.add_all(records)
        db.session.commit()
        _recordids = []
        for record in records:
            _recordids.append({"filename": record.filename, "recordid": record.recordid})
        return DefaultMethodResult(True,'Records created', -1, _recordids) 

    @classmethod
    def fetch(cls, foirequestid, ministryrequestid) -> DefaultMethodResult:
        records = []
        try:
            sql =   """select distinct on (fr1.recordid) recordid, fr1.filename, fr1.s3uripath, fr1."attributes" attributes, 
                            fr1.createdby createdby, fr1.created_at 
                            from "FOIRequestRecords" fr1
                            where fr1.foirequestid = :foirequestid and fr1.ministryrequestid = :ministryrequestid
                            order by recordid, version desc
                    """
            
            rs = db.session.execute(text(sql), {'foirequestid': foirequestid, 'ministryrequestid' : ministryrequestid})
           
            for row in rs:
                records.append({"recordid": row["recordid"], "filename": row["filename"], "s3uripath": row["s3uripath"],  "attributes": row["attributes"], "createdby": row["createdby"], "created_at": row["created_at"]})
            return records
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
    
class FOIRequestRecordSchema(ma.Schema):
    class Meta:
        fields = ('recordid','version','foirequestid','ministryrequestid','ministryrequestversion','attributes','filename','s3uripath','created_at','createdby','updated_at','updatedby') 