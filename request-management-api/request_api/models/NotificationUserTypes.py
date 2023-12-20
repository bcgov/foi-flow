from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text
import json
f = open('common/notificationusertypes.json', encoding="utf8")
notificationusertypes_cache = json.load(f)


class NotificationUserType(db.Model):
    __tablename__ = 'NotificationUserTypes' 
    # Defining the columns
    notificationusertypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    description = db.Column(db.String(255), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    notificationusertypelabel = db.Column(db.String(100), unique=True, nullable=False)

    @classmethod
    def getnotificationusertypes(cls):
        usertype_schema = NotificationUserTypeSchema(many=True)
        query = db.session.query(NotificationUserType).filter_by(isactive=True).all()
        return usertype_schema.dump(query)
    
    # create a class method that returns the notification type id
    @classmethod
    def getnotificationusertypesid(cls, notificationusertype):
        print("notificationusertype", notificationusertype)
        notificationusertypelabel = None
        for usertype in notificationusertypes_cache:
            if (notificationusertypes_cache[usertype]['name'] == notificationusertype) or (notificationusertypes_cache[usertype]['notificationusertypelabel'] == notificationusertype):
                notificationusertypelabel = notificationusertypes_cache[usertype]['notificationusertypelabel']
        if notificationusertypelabel is None:
            return None
        print("notificationusertypelabel", notificationusertypelabel)        
        type_schema = NotificationUserTypeSchema(many=False)
        query = db.session.query(NotificationUserType).filter_by(notificationusertypelabel=notificationusertypelabel, isactive=True).first()
        return type_schema.dump(query) if query is not None else None


class NotificationUserTypeSchema(ma.Schema):
    class Meta:
        fields = ('notificationusertypeid', 'notificationusertypelabel', 'name', 'description','isactive')