from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON
import json

class UnopenedReport(db.Model):
    __tablename__ = 'UnopenedReport' 
    # Defining the columns
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    rawrequestid = db.Column(db.Text, unique=False, nullable=False)
    date = db.Column(db.Text, unique=False, nullable=False)
    rank = db.Column(db.Text, unique=False, nullable=False)
    potentialmatches = db.Column(JSON, unique=False, nullable=False)
    
    @classmethod
    def bulkinsert(cls, rows):
        for row in rows:
            db.session.add(row)
        db.session.commit()
        return DefaultMethodResult(True,'Report Rows added',map(lambda row: row.rawrequestid, rows))