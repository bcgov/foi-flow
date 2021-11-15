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
class FOIRawRequestComment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestComments' 
    # Defining the columns
    commentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    requestid =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.requestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))
    comment = db.Column(db.String(1000), unique=False, nullable=True)  
    parentcommentid = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    commenttypeid = db.Column(db.Integer, unique=False, nullable=False)
    #commenttype =  relationship("CommentType",backref=backref("CommentTypes"),uselist=False)
    
    @classmethod
    def savecomment(cls, commenttypeid, foirequestcomment, version, userid)->DefaultMethodResult:   
        parentcommentid = foirequestcomment["parentcommentid"] if 'parentcommentid' in foirequestcomment  else None
        newcomment = FOIRawRequestComment(commenttypeid=commenttypeid, requestid=foirequestcomment["requestid"], version=version, comment=foirequestcomment["comment"], parentcommentid=parentcommentid, isactive=True, created_at=datetime.now(), createdby=userid)
        db.session.add(newcomment)
        db.session.commit()               
        return DefaultMethodResult(True,'Comment added',newcomment.commentid)          

    @classmethod
    def disablecomment(cls, commentid, userid):   
        dbquery = db.session.query(FOIRawRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0) :             
            comment.update({FOIRawRequestComment.isactive:False, FOIRawRequestComment.updatedby:userid, FOIRawRequestComment.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment disabled',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid)

    @classmethod
    def updatecomment(cls, commentid, foirequestcomment, userid):   
        dbquery = db.session.query(FOIRawRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0) :             
            comment.update({FOIRawRequestComment.isactive:True, FOIRawRequestComment.comment:foirequestcomment["comment"], FOIRawRequestComment.updatedby:userid, FOIRawRequestComment.updated_at:datetime.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment updated',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid)
            
    @classmethod
    def getcomments(cls, requestid)->DefaultMethodResult:   
        comment_schema = FOIRawRequestCommentSchema(many=True)
        query = db.session.query(FOIRawRequestComment).filter_by(requestid=requestid, isactive = True).order_by(FOIRawRequestComment.commentid.asc()).all()
        return comment_schema.dump(query)   
    
class FOIRawRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('commentid', 'requestid', 'parentcommentid','comment', 'commenttypeid','commenttype','isactive','created_at','createdby','updated_at','updatedby') 