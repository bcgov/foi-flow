from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text

import json
class FOIRawRequestNotificationUser(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestNotificationUsers' 
    # Defining the columns
    notificationuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    notificationid = db.Column(db.Integer,ForeignKey('FOIRawRequestNotifications.notificationid'))
    userid = db.Column(db.String(100), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationusertypeid = db.Column(db.Integer,nullable=False)

    @classmethod
    def dismissnotification(cls, notificationuserid):
        exists = bool(db.session.query(FOIRawRequestNotificationUser.notificationuserid).filter_by(notificationuserid=notificationuserid).first())
        if exists == False:
            return DefaultMethodResult(False,'Invalid ID',notificationuserid)
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationuserid == notificationuserid).delete()
        db.session.commit()  
        return DefaultMethodResult(True,'Notification deleted',notificationuserid)

    @classmethod
    def dismissnotificationbyuser(cls, userid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid).delete()
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypeid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid, FOIRawRequestNotificationUser.notificationusertypeid == notificationusertypeid).delete()
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod 
    def getnotificationsbyid(cls, notificationuserid):
        sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where notificationuserid  = :notificationuserid) group by notificationid """
        rs = db.session.execute(text(sql), {'notificationuserid': notificationuserid})
        notifications = []
        for row in rs:
            notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        return notifications
    
    @classmethod 
    def getnotificationsbyuser(cls, userid):
        sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid) group by notificationid """
        rs = db.session.execute(text(sql), {'userid': userid})
        notifications = []
        for row in rs:
            notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        return notifications

    @classmethod 
    def getnotificationsbyuserandtype(cls, userid, notificationusertypeid):
        sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid and notificationusertypeid = :notificationusertypeid) group by notificationid """
        rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypeid': notificationusertypeid})
        notifications = []
        for row in rs:
            notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        return notifications

    @classmethod
    def deletebynotificationid(cls, notificationids):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationid.in_(notificationids)).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids)  
    
class FOIRawRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid','created_at','createdby','updated_at','updatedby') 