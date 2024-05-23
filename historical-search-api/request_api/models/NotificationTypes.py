from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class NotificationType(db.Model):
    __tablename__ = 'NotificationTypes' 
    # Defining the columns
    notificationtypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    description = db.Column(db.String(255), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    notificationtypelabel = db.Column(db.String(100), unique=True, nullable=False)  

    @classmethod
    def getnotificationtypes(cls):
        type_schema = NotificationTypeSchema(many=True)
        query = db.session.query(NotificationType).filter_by(isactive=True).all()
        return type_schema.dump(query)
    
    # create a class method that returns the notification type id
    @classmethod
    def getnotificationtypeid(cls, notificationtype):
        type_schema = NotificationTypeSchema(many=False)
        query = db.session.query(NotificationType).filter_by(name=notificationtype, isactive=True).first()
        return type_schema.dump(query) if query is not None else None


class NotificationTypeSchema(ma.Schema):
    class Meta:
        fields = ('notificationtypeid', 'name', 'description','isactive', 'notificationtypelabel')

