from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2, timezone
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json
from sqlalchemy.sql.sqltypes import DateTime, String, Date, Integer
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import insert, and_, or_, text, func, literal, cast, asc, desc, case, nullsfirst, nullslast, TIMESTAMP, extract
from .FOIRawRequestNotifications import FOIRawRequestNotification
from .FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup
from request_api.models.views.FOINotifications import FOINotifications
from request_api.models.views.FOIRawRequests import FOIRawRequests


class FOIRawRequestNotificationUser(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestNotificationUsers' 
    # Defining the columns
    notificationuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    notificationid = db.Column(db.Integer,ForeignKey('FOIRawRequestNotifications.notificationid'))
    userid = db.Column(db.String(100), unique=False, nullable=True)
    isdeleted = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationusertypelabel = db.Column(db.Integer,nullable=False)


    @classmethod
    def dismissnotification(cls, notificationuserid, userid='system'):
        exists = bool(db.session.query(FOIRawRequestNotificationUser.notificationuserid).filter_by(notificationuserid=notificationuserid).first())
        if exists == False:
            return DefaultMethodResult(False,'Invalid ID',notificationuserid)
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationuserid == notificationuserid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notification deleted',notificationuserid)

    @classmethod
    def dismissnotificationbyuser(cls, userid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypelabel):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid, FOIRawRequestNotificationUser.notificationusertypelabel == notificationusertypelabel).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod 
    def getnotificationsbyid(cls, notificationuserid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where notificationuserid  = :notificationuserid) group by notificationid """
            rs = db.session.execute(text(sql), {'notificationuserid': notificationuserid})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications
    
    @classmethod 
    def getnotificationsbyuser(cls, userid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications

    @classmethod 
    def getnotificationsbyuserandtype(cls, userid, notificationusertypelabel):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid and notificationusertypelabel = :notificationusertypelabel) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypelabel': notificationusertypelabel})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications

    @classmethod
    def dismissbynotificationid(cls, notificationids, userid='system'):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationid.in_(notificationids)).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()}, synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids)  
     
    @classmethod
    def getnotificationidsbyuserandid(cls, userid, notificationids):
        ids = []
        try:
            sql = """select notificationid from "FOIRawRequestNotificationUsers" where userid = :userid and notificationid = ANY(:notificationids) """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationids': notificationids})
            for row in rs:
                ids.append(row["notificationid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return ids
    
    # Begin of Dashboard functions

    @classmethod
    def getbasequery(cls, groups, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False):
        _session = db.session

        selectedcolumns = [      
            FOIRawRequests.crtid.label('crtid'),        
            FOIRawRequests.axisrequestid.label('axisRequestId'),  
            FOIRawRequests.rawrequestid.label('rawrequestid'),
            FOIRawRequests.foirequest_id.label('requestid'),
            FOIRawRequests.ministryrequestid.label('ministryrequestid'),            
            FOIRawRequests.status.label('status'),        
            FOIRawRequests.assignedtoformatted.label('assignedToFormatted'), 
            FOIRawRequests.ministryassignedtoformatted.label('ministryAssignedToFormatted'),
            FOIRawRequests.description.label('description'),
            FOINotifications.notificationtype.label('notificationtype'),
            FOINotifications.notification.label('notification'),
            FOINotifications.created_at.label('createdat'),
            FOINotifications.createdatformatted.label('createdatformatted'),
            FOINotifications.userformatted.label('userFormatted'),
            FOINotifications.creatorformatted.label('creatorFormatted'),
            FOINotifications.id.label('id')          
        ]

        basequery = _session.query(
                                        *selectedcolumns
                                ).join(
                                        FOIRawRequests,
                                        and_(FOIRawRequests.axisrequestid == FOINotifications.axisnumber),
                                )
        
        if additionalfilter is not None:
            if(additionalfilter == 'watchingRequests' and userid is not None):
                #watchby
                subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)
                return basequery.join(subquery_watchby, subquery_watchby.c.requestid == cast(FOIRawRequests.rawrequestid, Integer))
            elif(additionalfilter == 'myRequests'):
                #myrequest
                return basequery.filter(or_(FOIRawRequests.assignedto == userid, and_(FOINotifications.userid == userid, FOINotifications.notificationtypelabel == 10)))
            else:
                if(isiaorestrictedfilemanager == True):
                    return basequery.filter(FOIRawRequests.assignedgroup.in_(groups))
                else:
                    return basequery.filter(
                        and_(
                            or_(FOIRawRequests.isiaorestricted.is_(None), FOIRawRequests.isiaorestricted == False, and_(FOIRawRequests.isiaorestricted == True, FOIRawRequests.assignedto == userid)))).filter(FOIRawRequests.assignedgroup.in_(groups))


    @classmethod
    def getrequestssubquery(cls, groups, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager):
        basequery = FOIRawRequestNotificationUser.getbasequery(groups, additionalfilter, userid, isiaorestrictedfilemanager)
        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = FOIRawRequestNotificationUser.getfilterforrequestssubquery(filterfields, keyword)
            return basequery.filter(filtercondition)
        else:
            return basequery
        
    @classmethod
    def getfilterforrequestssubquery(cls, filterfields, keyword):
        keyword = keyword.lower()
        #filter/search
        filtercondition = []
        if(keyword != 'restricted'):
            for field in filterfields:
                _keyword = FOIRawRequestNotificationUser.getfilterkeyword(keyword, field)
                filtercondition.append(FOIRawRequestNotificationUser.findfield(field).ilike('%'+_keyword+'%'))
                filtercondition.append(FOIRawRequests.isiaorestricted == True)

        return or_(*filtercondition)
    
    
    
    @classmethod
    def getfilterkeyword(cls, keyword, field):
        _newkeyword = keyword
        if(field == 'idNumber'):
            _newkeyword = _newkeyword.replace('u-00', '')
        return _newkeyword
        
    @classmethod
    def findfield(cls, x):
        return {
            'axisRequestId' : FOIRawRequests.axisrequestid,
            'createdat': FOINotifications.created_at,
            'createdatformatted': FOINotifications.createdatformatted,
            'notification': FOINotifications.notification,
            'assignedToFormatted': FOIRawRequests.assignedtoformatted,
            'ministryAssignedToFormatted': FOIRawRequests.ministryassignedtoformatted,
            'userFormatted': FOINotifications.userformatted,
            'creatorFormatted': FOINotifications.creatorformatted
        }.get(x, cast(FOINotifications.axisnumber, String))
    
    
    @classmethod
    def getsorting(cls, sortingitems, sortingorders):
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                if(FOIRawRequestNotificationUser.validatefield(field)):
                    order = sortingorders.pop(0)
                    if(order == 'desc'):
                        sortingcondition.append(nullslast(desc(field)))
                    else:
                        sortingcondition.append(nullsfirst(asc(field)))
        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(desc('createdat'))

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(desc('createdat'))
        
        return sortingcondition
    
    @classmethod
    def validatefield(cls, x):
        validfields = [
            'notification',            
            'axisRequestId',
            'createdat',
            'assignedToFormatted',
            'ministryAssignedToFormatted',
            'userFormatted',
            'creatorFormatted'      
        ]
        if x in validfields:
            return True
        else:
            return False
    # End of Dashboard functions
        
class FOIRawRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypelabel','created_at','createdby','updated_at','updatedby') 