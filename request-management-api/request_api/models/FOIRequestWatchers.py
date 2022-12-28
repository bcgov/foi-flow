from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text, and_, func
import logging
import json
class FOIRequestWatcher(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestWatchers' 
    # Defining the columns
    watcherid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    watchedbygroup = db.Column(db.String(250), unique=False, nullable=True) 
    watchedby = db.Column(db.String(120), unique=False, nullable=True)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def savewatcher(cls, foirequestwatcher, version, userid)->DefaultMethodResult:                
        newwatcher = FOIRequestWatcher(ministryrequestid=foirequestwatcher["ministryrequestid"], version=version, watchedbygroup=foirequestwatcher["watchedbygroup"], watchedby=foirequestwatcher["watchedby"], isactive=foirequestwatcher["isactive"], createdby=userid)
        db.session.add(newwatcher)
        db.session.commit()               
        return DefaultMethodResult(True,'Request added')   

    @classmethod
    def savewatcherbygroups(cls, foirequestwatcher, version, userid, watchergroups)->DefaultMethodResult:             
        for group in watchergroups:
            foirequestwatcher["watchedbygroup"] = group
            newwatcher = FOIRequestWatcher(ministryrequestid=foirequestwatcher["ministryrequestid"], version=version, watchedbygroup=foirequestwatcher["watchedbygroup"], watchedby=foirequestwatcher["watchedby"], isactive=foirequestwatcher["isactive"], createdby=userid)
            db.session.add(newwatcher)
            db.session.commit()               
        return DefaultMethodResult(True,'Request added')

    @classmethod
    def getMinistrywatchers(cls, ministryrequestid):
        watchers = []                
        try:
            sql = 'select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive from "FOIRequestWatchers" where ministryrequestid=:ministryrequestid and watchedbygroup like \'%Ministry Team\' order by watchedby, watchedbygroup, created_at desc'
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})        
            for row in rs:
                if row["isactive"] == True:
                    watchers.append({"watchedby": row["watchedby"], "watchedbygroup": row["watchedbygroup"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return watchers 
    
    @classmethod
    def getNonMinistrywatchers(cls, ministryrequestid):
        watchers = []     
        try:           
            sql = 'select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive from "FOIRequestWatchers" where ministryrequestid=:ministryrequestid and watchedbygroup not like \'%Ministry Team\' order by watchedby, watchedbygroup, created_at desc'
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})        
            for row in rs:
                if row["isactive"] == True:
                    watchers.append({"watchedby": row["watchedby"], "watchedbygroup": row["watchedbygroup"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return watchers 

    @classmethod
    def isaiaoministryrequestwatcher(cls, ministryrequestid,userid):
        _iswatcher = False    
        try:           
            sql = 'select distinct on (watchedby, watchedbygroup) watchedby, watchedbygroup, isactive from "FOIRequestWatchers" where ministryrequestid=:ministryrequestid and watchedby=:watchedby and isactive=True and watchedbygroup not like \'%Ministry Team\' order by watchedby, watchedbygroup, created_at desc'
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid,'watchedby':userid})        
            num_results = rs.rowcount
            if int(num_results) > 0:
                _iswatcher = True
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return _iswatcher 

    @classmethod
    def getrequestidsbyuserid(cls, userid):
        #subquery for getting latest watching status
        subquery_max = db.session.query(FOIRequestWatcher.ministryrequestid, FOIRequestWatcher.watchedby ,func.max(FOIRequestWatcher.watcherid).label('max_watcherid')).group_by(FOIRequestWatcher.ministryrequestid, FOIRequestWatcher.watchedby).subquery()
        joincondition = [
            subquery_max.c.ministryrequestid == FOIRequestWatcher.ministryrequestid,
            subquery_max.c.watchedby == FOIRequestWatcher.watchedby,
            subquery_max.c.max_watcherid == FOIRequestWatcher.watcherid,
        ]

        return db.session.query(
                                FOIRequestWatcher.ministryrequestid
                            ).join(
                                subquery_max,
                                and_(*joincondition)
                            ).filter(and_(FOIRequestWatcher.watchedby == userid, FOIRequestWatcher.isactive == True)).subquery()

    @classmethod
    def disablewatchers(cls, ministryrequestid, userid):   
        dbquery = db.session.query(FOIRequestWatcher)
        requestraqw = dbquery.filter_by(ministryrequestid=ministryrequestid)
        if(requestraqw.count() > 0) :             
            requestraqw.update({FOIRequestWatcher.isactive:False, FOIRequestWatcher.updatedby:userid, FOIRequestWatcher.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Watchers disabled',ministryrequestid)
        else:
            return DefaultMethodResult(True,'No Watchers found',ministryrequestid)
            
class FOIRequestWatcherSchema(ma.Schema):
    class Meta:
        fields = ('watcherid', 'foirequestid', 'ministryrequestid', 'watchedbygroup','watchedby','isactive','created_at','createdby','updated_at','updatedby') 