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
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)
    replacementof = db.Column(db.Integer, unique=False, nullable=False)

    @classmethod
    def create(cls, records):
        db.session.add_all(records)
        db.session.commit()
        _recordids = {}
        for record in records:
            _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.recordid}
        return DefaultMethodResult(True,'Records created', -1, _recordids)

    @classmethod
    def fetch(cls, foirequestid, ministryrequestid):
        records = []
        try:
            sql =   """select distinct on (fr1.recordid) recordid, fr1.isactive, fr1.filename, 
                        fr1.s3uripath, fr1."attributes" attributes, json_extract_path_text("attributes" ::json,'batch') as batchid,
                        fr1.createdby createdby, fr1.created_at,fr1.replacementof
                        from public."FOIRequestRecords" fr1 
                        where fr1.foirequestid = :foirequestid and fr1.ministryrequestid = :ministryrequestid  
                        order by recordid desc, version desc
                    """

            rs = db.session.execute(text(sql), {'foirequestid': foirequestid, 'ministryrequestid' : ministryrequestid})

            for row in rs:
                if row["isactive"] == True:
                    _originalfile =''
                    _originalfilename =''
                    if row["replacementof"] is not None:                       
                        originalrecord = FOIRequestRecord.getrecordbyid(row["replacementof"])
                        _originalfile = originalrecord["s3uripath"]
                        _originalfilename = originalrecord["filename"]                        
                    records.append({
                            "recordid": row["recordid"], 
                            "filename": row["filename"], 
                            "s3uripath": row["s3uripath"],  
                            "attributes": row["attributes"], 
                            "batchid": row["batchid"], 
                            "createdby": row["createdby"], 
                            "created_at": row["created_at"],
                            "replacementof":row["replacementof"],
                            "originalfile" : _originalfile,
                            "originalfilename":_originalfilename
                        })
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return records

    @classmethod
    def getrecordbyid(cls, recordid)->DefaultMethodResult:
        comment_schema = FOIRequestRecordSchema(many=False)
        query = db.session.query(FOIRequestRecord).filter_by(recordid=recordid).order_by(FOIRequestRecord.version.desc()).first()
        return comment_schema.dump(query)
    
    @classmethod
    def replace(cls,replacingrecordid,records):
        replacingrecord = db.session.query(FOIRequestRecord).filter_by(recordid=replacingrecordid).order_by(FOIRequestRecord.version.desc()).first()
        replacingrecord.isactive=False
        db.session.commit()
        db.session.add_all(records)
        db.session.commit() 
        _recordids = {}
        for record in records:
            _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.recordid}
        return DefaultMethodResult(True,'Records replaced', -1, _recordids)
    
    @classmethod
    def getbatchcount(cls, ministryrequestid):
        batchcount = 0
        try:
            sql = """select  count(distinct
                        json_extract_path_text("attributes" ::json,'batch')) AS batch_count
                        FROM "FOIRequestRecords" r
						join (select max(version), recordid
								  from public."FOIRequestRecords"
								  group by recordid) r2 on r2.max = r.version and r2.recordid = r.recordid
                        where ministryrequestid = :ministryrequestid and isactive = true  """
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                batchcount = row["batch_count"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return batchcount

class FOIRequestRecordSchema(ma.Schema):
    class Meta:
        fields = ('recordid','version','foirequestid','ministryrequestid','ministryrequestversion','attributes','filename','s3uripath','created_at','createdby','updated_at','updatedby','replacementof')