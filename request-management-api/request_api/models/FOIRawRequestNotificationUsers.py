from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json
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

    notificationusertypeid = db.Column(db.Integer,nullable=False)

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
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypeid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid, FOIRawRequestNotificationUser.notificationusertypeid == notificationusertypeid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
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
    def getnotificationsbyuserandtype(cls, userid, notificationusertypeid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid and notificationusertypeid = :notificationusertypeid) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypeid': notificationusertypeid})
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
        
class FOIRawRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid','created_at','createdby','updated_at','updatedby') 