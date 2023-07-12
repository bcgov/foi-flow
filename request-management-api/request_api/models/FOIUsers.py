from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class FOIUser(db.Model):
    __tablename__ = 'FOIUsers' 
    # Defining the columns
    foiuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.Text, unique=False, nullable=False)
    preferred_username = db.Column(db.Text, unique=False, nullable=False)
    firstname = db.Column(db.Text, unique=False, nullable=False)
    lastname = db.Column(db.Text, unique=False, nullable=False)
    email = db.Column(db.Text, unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, default='System')
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    @classmethod
    def saveuser(cls, foiuser):
        db.session.add(foiuser)
        db.session.commit()
        return DefaultMethodResult(True,'User added',foiuser.preferred_username)


    @classmethod
    def updateeuser(cls, foiuser):
        try:
            dbquery = db.session.query(FOIUser)
            _user = dbquery.filter_by(username=foiuser.username)
            if(_user.count() > 0):
                _user.update({FOIUser.firstname: foiuser.firstname, 
                              FOIUser.lastname: foiuser.lastname, 
                              FOIUser.email: foiuser.email, 
                              FOIUser.preferred_username: foiuser.preferred_username, 
                              FOIUser.isactive:foiuser.isactive, 
                              FOIUser.updated_at:datetime.now(), FOIUser.updatedby:"System"}, synchronize_session = False)
                db.session.commit()
                return DefaultMethodResult(True,'User updated for Id',FOIUser.preferred_username)
        except:
            db.session.rollback()
            raise

    @classmethod
    def getall(cls):
        user_schema = UserSchema(many=True)
        query = db.session.query(FOIUser).order_by(FOIUser.foiuserid.asc()).all()
        return user_schema.dump(query)        

class UserSchema(ma.Schema):
    class Meta:
        fields = ('foiuserid','username','preferred_username','firstname','lastname','email','isactive')