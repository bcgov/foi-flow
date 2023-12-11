from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime as datetime2, timedelta
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json
class FOIRawRequestNotification(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestNotifications' 
      # Defining the columns
    notificationid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    requestid =db.Column(db.Integer,  db.ForeignKey('FOIRawRequests.requestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))    
    idnumber = db.Column(db.String(50), unique=False, nullable=True)
    axisnumber = db.Column(db.String(50), unique=False, nullable=True)
    notification = db.Column(JSON, unique=False, nullable=True)
    isdeleted = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationtypelabel = db.Column(db.Integer, nullable=False)
    
    notificationusers = db.relationship('FOIRawRequestNotificationUser', backref='FOIRawRequestNotifications', lazy='dynamic')

        
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
    def dismissnotification(cls, notificationids, userid='system'):
        try:
            db.session.query(FOIRawRequestNotification).filter(FOIRawRequestNotification.notificationid.in_(notificationids)).update({FOIRawRequestNotification.isdeleted: True, FOIRawRequestNotification.updatedby: userid,
                            FOIRawRequestNotification.updated_at: datetime2.now()}, synchronize_session=False)
            db.session.commit()  
            return DefaultMethodResult(True,'Notifications deleted ', notificationids)
        except:
            db.session.rollback()
            raise

    @classmethod
    def updatenotification(cls, foinotification, userid):
        dbquery = db.session.query(FOIRawRequestNotification)
        _notification = dbquery.filter_by(notificationid=foinotification['notificationid'])
        if(_notification.count() > 0) :
            _notification.update({
                FOIRawRequestNotification.notification:foinotification['notification'],
                FOIRawRequestNotification.updatedby:userid,
                FOIRawRequestNotification.updated_at:datetime2.now()
            }, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'notification updated',foinotification['notificationid'])
        else:
            return DefaultMethodResult(True,'No notification found',foinotification['notificationid'])
        
    @classmethod
    def getnotificationidsbynumberandtype(cls, idnumber, notificationtypelabel):
        notificationids = []
        try:
            sql = """select notificationid from "FOIRawRequestNotifications" where idnumber = :idnumber and notificationtypelabel= :notificationtypelabel """
            rs = db.session.execute(text(sql), {'idnumber': idnumber, 'notificationtypelabel': notificationtypelabel})
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
            sql = """select notificationid from "FOIRawRequestNotifications" where idnumber = :idnumber """
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
        notificationids = []
        try:
            sql = """select notificationid from "FOIRawRequestNotifications" where notificationtypelabel= :notificationtypelabel """
            rs = db.session.execute(text(sql), {'notificationtypelabel': notificationtypelabel})
            for row in rs:
                notificationids.append(row["notificationid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notificationids
    
class FOIRawRequestNotificationSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'requestid', 'idnumber','notification', 'notificationtypeid', 'notificationtypelabel','created_at','createdby','updated_at','updatedby','notificationusers') 