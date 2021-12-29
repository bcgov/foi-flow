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
class FOIRequestNotificationUser(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestNotificationUsers' 
    # Defining the columns
    notificationuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    notificationid = db.Column(db.Integer,ForeignKey('FOIRequestNotifications.notificationid'))
    userid = db.Column(db.String(100), unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationusertypeid = db.Column(db.Integer,nullable=False)

    @classmethod
    def dismissnotification(cls, notificationuserid):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.notificationuserid == notificationuserid).delete()
        db.session.commit()  
        return DefaultMethodResult(True,'Notification deleted',notificationuserid)
    
    @classmethod
    def dismissnotificationbyuser(cls, userid):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.userid == userid).delete()
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)
class FOIRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid','created_at','createdby','updated_at','updatedby') 