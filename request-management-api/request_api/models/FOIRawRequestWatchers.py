from enum import unique


from sqlalchemy.sql.expression import distinct
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON, UUID
from .default_method_result import DefaultMethodResult
from datetime import datetime
from sqlalchemy import insert, and_, text
from flask import jsonify

class FOIRawRequestWatcher(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestWatchers' 
    # Defining the columns
    watcherid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    requestid =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.requestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))
    watchedbygroup = db.Column(db.String(250), unique=False, nullable=True) 
    watchedby = db.Column(db.String(120), unique=False, nullable=True)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def savewatcher(cls, foirawrequestwatcher, version, userid)->DefaultMethodResult:             
        newwatcher = FOIRawRequestWatcher(requestid=foirawrequestwatcher["requestid"], version=version, watchedbygroup=foirawrequestwatcher["watchedbygroup"], watchedby=foirawrequestwatcher["watchedby"], isactive=foirawrequestwatcher["isactive"], created_at=datetime.now(), createdby=userid)
        db.session.add(newwatcher)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added',newwatcher.watcherid)
    
    
    @classmethod
    def getwatchers(cls, requestid):                
        sql = 'select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive from "FOIRawRequestWatchers" where requestid=:requestid order by watchedby, watchedbygroup, created_at desc'
        rs = db.session.execute(text(sql), {'requestid': requestid})
        watchers = []
        for row in rs:
            if row["isactive"] == True:
                watchers.append({"watchedby": row["watchedby"], "watchedbygroup": row["watchedbygroup"]})
        return watchers 

    @classmethod
    def disablewatchers(cls, requestid, userid):   
        dbquery = db.session.query(FOIRawRequestWatcher)
        requestraqw = dbquery.filter_by(requestid=requestid)
        if(requestraqw.count() > 0) :             
            requestraqw.update({FOIRawRequestWatcher.isactive:False, FOIRawRequestWatcher.updatedby:userid, FOIRawRequestWatcher.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Watchers disabled',requestid)
        else:
            return DefaultMethodResult(True,'No Watchers found',requestid)

class FOIRawRequestWatcherSchema(ma.Schema):
    class Meta:
        fields = ('watcherid', 'requestid', 'watchedbygroup','watchedby','isactive','created_at','createdby','updated_at','updatedby')