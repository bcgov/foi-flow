from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class CommentType(db.Model):
    __tablename__ = 'CommentTypes' 
    # Defining the columns
    commenttypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    label= db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getcommenttypes(cls):
        commenttype_schema = CommentTypeSchema(many=True)
        query = db.session.query(CommentType).filter_by(isactive=True).all()
        return commenttype_schema.dump(query)
    
    @classmethod
    def getcommenttypeidbyname(cls, name):
        commenttype_schema = CommentTypeSchema()
        query = db.session.query(CommentType).filter_by(name= name , isactive=True).first()
        return commenttype_schema.dump(query)


class CommentTypeSchema(ma.Schema):
    class Meta:
        fields = ('commenttypeid', 'name', 'label', 'description','isactive')