from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class NotificationUserType(db.Model):
    __tablename__ = 'NotificationUserTypes' 
    # Defining the columns
    notificationusertypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    description = db.Column(db.String(255), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getnotificationusertypes(cls):
        usertype_schema = NotificationUserTypeSchema(many=True)
        query = db.session.query(NotificationUserType).filter_by(isactive=True).all()
        return usertype_schema.dump(query)


class NotificationUserTypeSchema(ma.Schema):
    class Meta:
        fields = ('notificationusertypeid', 'name', 'description','isactive')