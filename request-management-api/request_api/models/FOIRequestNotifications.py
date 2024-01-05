import logging
from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import maya
import json
f = open('common/notificationtypes.json', encoding="utf8")
notificationtypes_cache = json.load(f)

class FOIRequestNotification(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestNotifications' 
      # Defining the columns
    notificationid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    foirequestid =db.Column(db.Integer,  nullable=False)
    requestid =db.Column(db.Integer,  db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    idnumber = db.Column(db.String(50), unique=False, nullable=True)
    axisnumber = db.Column(db.String(50), unique=False, nullable=True)
    notification = db.Column(JSON, unique=False, nullable=True)
    isdeleted = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    notificationtypeid = db.Column(db.Integer, nullable=False)
    notificationtypelabel = db.Column(db.String(50), nullable=False)
    
    notificationusers = db.relationship('FOIRequestNotificationUser', backref='FOIRequestNotifications', lazy='dynamic')

        
    @classmethod
    def savenotification(cls,foinotification)->DefaultMethodResult:
        try:
            db.session.add(foinotification)
            db.session.commit()        
            return DefaultMethodResult(True,'Notification added',foinotification.requestid)    
        except:
            db.session.rollback()
            raise

    @classmethod
    def updatenotification(cls, foinotification, userid):
        dbquery = db.session.query(FOIRequestNotification)
        _notification = dbquery.filter_by(notificationid=foinotification['notificationid'])
        if(_notification.count() > 0) :
            _notification.update({
                FOIRequestNotification.notification:foinotification['notification'],
                FOIRequestNotification.updatedby:userid,
                FOIRequestNotification.updated_at:datetime2.now()
            }, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'notification updated',foinotification['notificationid'])
        else:
            return DefaultMethodResult(True,'No notification found',foinotification['notificationid'])
        

    @classmethod 
    def getconsolidatednotifications(cls, userid, days):
        notifications = []
        try:
            sql = """select idnumber, axisnumber, notificationid, notification , notificationtype, userid, notificationusertype, created_at, createdby, requesttype, requestid, foirequestid from (   
                    select frn.idnumber, frn.axisnumber, frn.requestid, frns.notificationuserid as notificationid, frn.notification -> 'message' as notification , nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'ministryrequest' requesttype, frn.foirequestid from "FOIRequestNotifications" frn inner join "FOIRequestNotificationUsers" frns on frn.notificationid = frns.notificationid and frns.isdeleted = false inner join "NotificationTypes" nty on frn.notificationtypelabel = nty.notificationtypelabel inner join "NotificationUserTypes" ntu on frns.notificationusertypelabel = ntu.notificationusertypelabel where frns.userid=:userid and frn.created_at  >= current_date - interval :days day
                    union all
                    select frn.idnumber, frn.axisnumber, frn.requestid, frns.notificationuserid as notificationid, frn.notification -> 'message' as notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'rawrequest' requesttype, 0 foirequestid  from "FOIRawRequestNotifications" frn inner join "FOIRawRequestNotificationUsers" frns on frn.notificationid = frns.notificationid and frns.isdeleted = false inner join "NotificationTypes" nty on frn.notificationtypelabel = nty.notificationtypelabel inner join "NotificationUserTypes" ntu on frns.notificationusertypelabel = ntu.notificationusertypelabel where frns.userid=:userid and frn.created_at  >= current_date - interval :days day
                  ) as notf order by created_at desc"""
            rs = db.session.execute(text(sql), {'userid': userid, 'days': days})
            for row in rs:
                dt = maya.parse(row["created_at"]).datetime(to_timezone='America/Vancouver', naive=False)
                _createddate = dt
                notifications.append({"idnumber": row["idnumber"], "axisnumber": row["axisnumber"], "notificationid": row["notificationid"], "notification": row["notification"], "notificationtype": row["notificationtype"],  "notificationusertype": row["notificationusertype"], "created_at": _createddate.strftime('%Y %b %d | %I:%M %p').upper(), "createdby": row["createdby"], "requesttype":row["requesttype"], "requestid":row["requestid"],"foirequestid":row["foirequestid"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications
    
    @classmethod 
    def getcommentnotifications(cls, commentid):
        notifications = []
        try:
            sql = """select idnumber, axisnumber, notificationid, notificationuserid, notification , notificationtype, userid, notificationusertype, created_at, createdby, requesttype, requestid, foirequestid from (   
                    select frn.idnumber, frn.axisnumber, frn.requestid, frn.notificationid, frns.notificationuserid, frn.notification -> 'message' as notification , nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'ministryrequest' requesttype, frn.foirequestid from "FOIRequestNotifications" frn inner join "FOIRequestNotificationUsers" frns on frn.notificationid = frns.notificationid and frns.isdeleted = false  inner join "NotificationTypes" nty on frn.notificationtypelabel = nty.notificationtypelabel inner join "NotificationUserTypes" ntu on frns.notificationusertypelabel = ntu.notificationusertypelabel where frn.notificationtypelabel in :notificationtypelabel and (frn.notification ->> 'commentid')::int = :commentid
                    union all
                    select frn.idnumber, frn.axisnumber, frn.requestid, frn.notificationid, frns.notificationuserid, frn.notification -> 'message' as notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'rawrequest' requesttype, 0 foirequestid  from "FOIRawRequestNotifications" frn inner join "FOIRawRequestNotificationUsers" frns on frn.notificationid = frns.notificationid and frns.isdeleted = false  inner join "NotificationTypes" nty on frn.notificationtypelabel = nty.notificationtypelabel inner join "NotificationUserTypes" ntu on frns.notificationusertypelabel = ntu.notificationusertypelabel where frn.notificationtypelabel in :notificationtypelabel and (frn.notification ->> 'commentid')::int = :commentid
                  ) as notf order by created_at desc"""
            notificationtypelabel = tuple([notificationtypes_cache['newusercomments']['notificationtypelabel'],
                                     notificationtypes_cache['replyusercomments']['notificationtypelabel'],
                                     notificationtypes_cache['taggedusercomments']['notificationtypelabel'],
                                     ]) # 3,9,10
            # notificationtypelabel = ','.join(str(e) for e in notificationtypelabel)
            rs = db.session.execute(text(sql), {'commentid': commentid, 'notificationtypelabel': notificationtypelabel})
            for row in rs:
                dt = maya.parse(row["created_at"]).datetime(to_timezone='America/Vancouver', naive=False)
                _createddate = dt
                notifications.append({"userid": row["userid"],"idnumber": row["idnumber"], "axisnumber": row["axisnumber"], "notificationid": row["notificationid"], "notificationuserid": row["notificationuserid"], "notification": row["notification"], "notificationtype": row["notificationtype"],  "notificationusertype": row["notificationusertype"], "created_at": _createddate.strftime('%Y %b %d | %I:%M %p').upper(), "createdby": row["createdby"], "requesttype":row["requesttype"], "requestid":row["requestid"],"foirequestid":row["foirequestid"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications
    
    @classmethod 
    def getextensionnotifications(cls, extensionid):
        notifications = []
        try:
            sql = sql = """select idnumber, axisnumber, notificationid, notification , notificationtypelabel from "FOIRequestNotifications" where isdeleted = false and notification->>'extensionid' = :extensionid """
            rs = db.session.execute(text(sql), {'extensionid': str(extensionid)})
            for row in rs:
                notifications.append({"idnumber": row["idnumber"], "axisnumber": row["axisnumber"], "notificationid": row["notificationid"], "notification": row["notification"], "notificationtypelabel": row["notificationtypelabel"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications

    @classmethod
    def dismissnotification(cls, notificationids, userid='system'):
        try:
            db.session.query(FOIRequestNotification).filter(FOIRequestNotification.notificationid.in_(notificationids), FOIRequestNotification.isdeleted == False).update({FOIRequestNotification.isdeleted: True, FOIRequestNotification.updatedby: userid,
                            FOIRequestNotification.updated_at: datetime2.now()}, synchronize_session=False)
            db.session.commit()  
            return DefaultMethodResult(True,'Notifications deleted ', notificationids)       
        except:
            db.session.rollback()
            raise
        
    @classmethod
    def getnotificationidsbynumberandtype(cls, idnumber, notificationtypelabels):
        notificationids = []
        try:
            sql = """select notificationid from "FOIRequestNotifications" where idnumber = :idnumber and notificationtypelabel = ANY(:notificationtypelabels) and isdeleted = false """
            rs = db.session.execute(text(sql), {'idnumber': idnumber, 'notificationtypelabels': notificationtypelabels})
            for row in rs:
                notificationids.append(row["notificationid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notificationids

    @classmethod
    def getnotificationidsbynumber(cls, idnumber):
        notificationids = []
        try:
            sql = """select notificationid from "FOIRequestNotifications" where idnumber = :idnumber and isdeleted = false """
            rs = db.session.execute(text(sql), {'idnumber': idnumber})
            for row in rs:
                notificationids.append(row["notificationid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notificationids

    @classmethod
    def getnotificationidsbytype(cls, notificationtypelabel):
        sql = """select notificationid from "FOIRequestNotifications" where notificationtypelabel= :notificationtypelabel and isdeleted = false """
        rs = db.session.execute(text(sql), {'notificationtypelabel': notificationtypelabel})
        notificationids = []
        for row in rs:
            notificationids.append(row["notificationid"])
        return notificationids
    
    @classmethod
    def getextensionnotificationidsbyministry(cls, ministryid):
        sql = """select notificationid from "FOIRequestNotifications" where requestid = :requestid and notificationtypelabel = 4 and isdeleted = false """
        rs = db.session.execute(text(sql), {'requestid': ministryid})
        notificationids = []
        for row in rs:
            notificationids.append(row["notificationid"])
        return notificationids

class FOIRequestNotificationSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'ministryrequestid', 'notification', 'notificationtypeid', 'notificationtypelabel','created_at','createdby','updated_at','updatedby') 