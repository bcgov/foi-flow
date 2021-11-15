from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text

import json
class FOIRequestComment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestComments' 
    # Defining the columns
    commentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    comment = db.Column(db.String(1000), unique=False, nullable=True)  
    parentcommentid = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    commenttypeid = db.Column(db.Integer, unique=False, nullable=False)
    #commenttypeid =  relationship("CommentType",backref=backref("CommentTypes"),uselist=False)
 
    
    @classmethod
    def savecomment(cls, commenttypeid, foirequestcomment, version, userid,commentcreatedate=None)->DefaultMethodResult:   
        parentcommentid = foirequestcomment["parentcommentid"] if 'parentcommentid' in foirequestcomment  else None
        _createdDate = datetime.now() if commentcreatedate is None else commentcreatedate
        newcomment = FOIRequestComment(commenttypeid=commenttypeid, ministryrequestid=foirequestcomment["ministryrequestid"], version=version, comment=foirequestcomment["comment"], parentcommentid=parentcommentid, isactive=True, created_at= _createdDate, createdby=userid)
        db.session.add(newcomment)
        db.session.commit()               
        return DefaultMethodResult(True,'Comment added',newcomment.commentid)    

    @classmethod
    def disablecomment(cls, commentid, userid):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0) :             
            comment.update({FOIRequestComment.isactive:False, FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment disabled',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid)  
        
    @classmethod
    def updatecomment(cls, commentid, foirequestcomment, userid):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0) :             
            comment.update({FOIRequestComment.isactive:True, FOIRequestComment.comment:foirequestcomment["comment"], FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment updated',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid)
            
    @classmethod
    def getcomments(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestComment).filter_by(ministryrequestid=ministryrequestid, isactive = True).order_by(FOIRequestComment.commentid.desc()).all()
        return comment_schema.dump(query)   
    
class FOIRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('commentid', 'ministryrequestid', 'parentcommentid','comment', 'commenttypeid','commenttype','isactive','created_at','createdby','updated_at','updatedby') 