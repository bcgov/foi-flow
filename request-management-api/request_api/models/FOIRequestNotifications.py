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
        return DefaultMethodResult(True,'Request added',foinotification.requestid)

    @classmethod 
    def getconsolidatednotifications(cls, userid):
        sql = """select idnumber, notificationid, notification , notificationtype, userid, notificationusertype, created_at, createdby from (   
                    select frn.idnumber, frns.notificationuserid as notificationid, frn.notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype  from "FOIRequestNotifications" frn inner join "FOIRequestNotificationUsers" frns on frn.notificationid = frns.notificationid inner join "NotificationTypes" nty on frn.notificationtypeid = nty.notificationtypeid inner join "NotificationUserTypes" ntu on frns.notificationusertypeid = ntu.notificationusertypeid where frns.userid=:userid and frn.created_at  >= current_date - interval '10' day
                    union all
                    select frn.idnumber, frns.notificationuserid as notificationid, frn.notification, nty.name as notificationtype, frn.created_at , frns.createdby, frns.userid, ntu.name as notificationusertype  from "FOIRawRequestNotifications" frn inner join "FOIRawRequestNotificationUsers" frns on frn.notificationid = frns.notificationid inner join "NotificationTypes" nty on frn.notificationtypeid = nty.notificationtypeid inner join "NotificationUserTypes" ntu on frns.notificationusertypeid = ntu.notificationusertypeid where frns.userid=:userid and frn.created_at  >= current_date - interval '10' day
                  ) as notf order by created_at desc"""
        rs = db.session.execute(text(sql), {'userid': userid})
        notifications = []
        for row in rs:
            notifications.append({"idnumber": row["idnumber"], "notificationid": row["notificationid"], "notification": row["notification"], "notificationtype": row["notificationtype"],  "notificationusertype": row["notificationusertype"], "created_at": row["created_at"].strftime('%Y-%m-%d %H:%M:%S.%f'), "createdby": row["createdby"]})
        return notifications

       

class FOIRequestNotificationSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'ministryrequestid', 'notification', 'notificationtypeid','created_at','createdby','updated_at','updatedby') 