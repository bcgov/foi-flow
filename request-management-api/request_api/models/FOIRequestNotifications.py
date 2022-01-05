from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import maya

import json
class FOIRequestNotification(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestNotifications' 
      # Defining the columns
    notificationid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    foirequestid =db.Column(db.Integer,  nullable=False)
    requestid =db.Column(db.Integer,  db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))    
    idnumber = db.Column(db.String(50), unique=False, nullable=True)
    notification = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationtypeid = db.Column(db.Integer, nullable=False)
    
    notificationusers = db.relationship('FOIRequestNotificationUser', backref='FOIRequestNotifications', lazy='dynamic')

        
    @classmethod
    def savenotification(cls,foinotification)->DefaultMethodResult:
        db.session.add(foinotification)
        db.session.commit()
        return DefaultMethodResult(True,'Notification added',foinotification.requestid)

    @classmethod 
    def getconsolidatednotifications(cls, userid, days):
        sql = """select idnumber, notificationid, notification , notificationtype, userid, notificationusertype, created_at, createdby, requesttype, requestid, foirequestid from (   
                    select frn.idnumber, frn.requestid, frns.notificationuserid as notificationid, frn.notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'ministryrequest' requesttype, frn.foirequestid from "FOIRequestNotifications" frn inner join "FOIRequestNotificationUsers" frns on frn.notificationid = frns.notificationid inner join "NotificationTypes" nty on frn.notificationtypeid = nty.notificationtypeid inner join "NotificationUserTypes" ntu on frns.notificationusertypeid = ntu.notificationusertypeid where frns.userid=:userid and frn.created_at  >= current_date - interval :days day
                    union all
                    select frn.idnumber, frn.requestid, frns.notificationuserid as notificationid, frn.notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype, 'rawrequest' requesttype, 0 foirequestid  from "FOIRawRequestNotifications" frn inner join "FOIRawRequestNotificationUsers" frns on frn.notificationid = frns.notificationid inner join "NotificationTypes" nty on frn.notificationtypeid = nty.notificationtypeid inner join "NotificationUserTypes" ntu on frns.notificationusertypeid = ntu.notificationusertypeid where frns.userid=:userid and frn.created_at  >= current_date - interval :days day
                  ) as notf order by created_at desc"""
        rs = db.session.execute(text(sql), {'userid': userid, 'days': days})
        notifications = []
        for row in rs:
            dt = maya.parse(row["created_at"]).datetime(to_timezone='America/Vancouver', naive=False)
            _createddate = dt
            notifications.append({"idnumber": row["idnumber"], "notificationid": row["notificationid"], "notification": row["notification"], "notificationtype": row["notificationtype"],  "notificationusertype": row["notificationusertype"], "created_at": _createddate.strftime('%Y %b %d | %I:%M %p').upper(), "createdby": row["createdby"], "requesttype":row["requesttype"], "requestid":row["requestid"],"foirequestid":row["foirequestid"]})
        return notifications

    @classmethod
    def dismissnotification(cls, notificationids):
        db.session.query(FOIRequestNotification).filter(FOIRequestNotification.notificationid.in_(notificationids)).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted ', notificationids)       

    @classmethod
    def deletebynotificationid(cls, notificationids):
        db.session.query(FOIRequestNotification).filter(FOIRequestNotification.notificationid.in_(notificationids)).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids) 

    @classmethod
    def getnotificationidsbynumber(cls, idnumber, notificationtypeid):
        sql = """select notificationid from "FOIRequestNotifications" where idnumber = :idnumber and notificationtypeid= :notificationtypeid """
        rs = db.session.execute(text(sql), {'idnumber': idnumber, 'notificationtypeid': notificationtypeid})
        notificationids = []
        for row in rs:
            notificationids.append(row["notificationid"])
        return notificationids


class FOIRequestNotificationSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'ministryrequestid', 'notification', 'notificationtypeid','created_at','createdby','updated_at','updatedby') 