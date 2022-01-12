from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2, timedelta
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text

import json
class FOIRawRequestNotification(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestNotifications' 
      # Defining the columns
    notificationid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    requestid =db.Column(db.Integer,  db.ForeignKey('FOIRawRequests.requestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))    
    idnumber = db.Column(db.String(50), unique=False, nullable=True)
    notification = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime2.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationtypeid = db.Column(db.Integer, nullable=False)
    
    notificationusers = db.relationship('FOIRawRequestNotificationUser', backref='FOIRawRequestNotifications', lazy='dynamic')

        
    @classmethod
    def savenotification(cls,foinotification)->DefaultMethodResult:
        db.session.add(foinotification)
        db.session.commit()
        return DefaultMethodResult(True,'Notification added',foinotification.requestid)
      
    @classmethod
    def dismissnotification(cls, notificationids):
        db.session.query(FOIRawRequestNotification).filter(FOIRawRequestNotification.notificationid.in_(notificationids)).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted ', notificationids)

    @classmethod
    def deletebynotificationid(cls, notificationids):
        db.session.query(FOIRawRequestNotification).filter(FOIRawRequestNotification.notificationid.in_(notificationids)).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids) 

    @classmethod
    def getnotificationidsbynumberandtype(cls, idnumber, notificationtypeid):
        sql = """select notificationid from "FOIRawRequestNotifications" where idnumber = :idnumber and notificationtypeid= :notificationtypeid """
        rs = db.session.execute(text(sql), {'idnumber': idnumber, 'notificationtypeid': notificationtypeid})
        notificationids = []
        for row in rs:
            notificationids.append(row["notificationid"])
        return notificationids
    
    @classmethod
    def getnotificationidsbynumber(cls, idnumber, notificationtypeid):
        sql = """select notificationid from "FOIRawRequestNotifications" where idnumber = :idnumber """
        rs = db.session.execute(text(sql), {'idnumber': idnumber})
        notificationids = []
        for row in rs:
            notificationids.append(row["notificationid"])
        return notificationids
    
class FOIRawRequestNotificationSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'requestid', 'idnumber','notification', 'notificationtypeid','created_at','createdby','updated_at','updatedby','notificationusers') 