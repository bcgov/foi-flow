from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text, insert
import logging
import json
class FOIRequestComment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestComments' 
    # Defining the columns
    commentid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    version =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    comment = db.Column(db.Text, unique=False, nullable=True)
    taggedusers = db.Column(JSON, unique=False, nullable=True)  
    parentcommentid = db.Column(db.Integer, db.ForeignKey('FOIRequestComments.commentid'), nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    parentcomment = relationship("FOIRequestComment", backref=backref("FOIRequestComments"), remote_side=[commentid], uselist=False)

    commenttypeid = db.Column(db.Integer, unique=False, nullable=False)
    commentsversion = db.Column(db.Integer, nullable=False)
 
    
    @classmethod
    def savecomment(cls, commenttypeid, foirequestcomment, version, userid,commentcreatedate=None)->DefaultMethodResult:
        commentsversion = 1
        parentcommentid = foirequestcomment["parentcommentid"] if 'parentcommentid' in foirequestcomment  else None
        taggedusers = foirequestcomment["taggedusers"] if 'taggedusers' in foirequestcomment  else None
        _createddate = datetime2.now().isoformat() if commentcreatedate is None else commentcreatedate        
        newcomment = FOIRequestComment(commenttypeid=commenttypeid, ministryrequestid=foirequestcomment["ministryrequestid"], version=version, comment=foirequestcomment["comment"], parentcommentid=parentcommentid, isactive=True, created_at=_createddate, createdby=userid,taggedusers=taggedusers, commentsversion=commentsversion)
        db.session.add(newcomment)
        db.session.commit()      
        return DefaultMethodResult(True,'Comment added',newcomment.commentid)    

    @classmethod
    def deleteextensioncommentsbyministry(cls, ministryid):
        db.session.query(FOIRequestComment).filter(FOIRequestComment.ministryrequestid == ministryid, FOIRequestComment.commenttypeid == 2).delete(synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Extensions comments deleted for the ministry ', ministryid)

    @classmethod
    def disablecomment(cls, commentid, userid, action=""):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid, isactive=True)
        if(comment.count() > 0) :             
            childcomments = dbquery.filter_by(parentcommentid=commentid, isactive=True)
            if (childcomments.count() > 0 and action != 'edit') :
                return DefaultMethodResult(False,'Cannot delete parent comment with replies',commentid)
            elif (childcomments.count() > 0 and action == 'edit'):
                childcomments.update({FOIRequestComment.isactive:False, FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime2.now()}, synchronize_session = False)
            comment.update({FOIRequestComment.isactive:False, FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment disabled',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid) 
        
    @classmethod
    def updatecomment(cls, commentid, foirequestcomment, userid):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid, isactive=True).first()
        if(comment.count() > 0) :
            existingtaggedusers = comment.first().taggedusers
            taggedusers = foirequestcomment["taggedusers"] if 'taggedusers' in foirequestcomment  else existingtaggedusers
            commentversion = int(comment.first().commentversion) + 1
            insertstmt = (insert(FOIRequestComment).values(
                commentid= comment.first().commentid,
                ministryrequestid=comment.first().ministryrequestid,
                version=comment.first().version,
                comment=foirequestcomment["comment"],
                taggedusers=taggedusers,
                parentcommentid=comment.first().parentcommentid,
                isactive=True,
                created_at=datetime2.now(),
                createdby=userid,
                updated_at=datetime2.now(),
                updatedby=userid,
                commenttypeid=comment.first().commenttypeid,
                commentversion=commentversion
            ))
            db.session.execute(insertstmt)            
            # comment.update({FOIRequestComment.isactive:True, FOIRequestComment.comment:foirequestcomment["comment"], FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime2.now(),FOIRequestComment.taggedusers:taggedusers}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Updated Comment added',commentid,existingtaggedusers)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid,existingtaggedusers)
            
    @classmethod
    def getcomments(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestComment).filter_by(ministryrequestid=ministryrequestid, isactive = True).order_by(FOIRequestComment.commentid.desc()).all()
        return comment_schema.dump(query)   

    @classmethod
    def getcommentbyid(cls, commentid) -> DefaultMethodResult:
        comment_schema = FOIRequestCommentSchema()
        query = db.session.query(FOIRequestComment).filter_by(commentid=commentid, isactive=True).first()
        return comment_schema.dump(query)
    
    @classmethod 
    def getcommentusers(cls, commentid):
        users = []
        try:
            sql = """select commentid, createdby, taggedusers from (
                        select commentid, commenttypeid, createdby, taggedusers from "FOIRequestComments" frc   where commentid = (select parentcommentid from "FOIRequestComments" frc   where commentid=:commentid) and isactive = true
                        union all 
                        select commentid, commenttypeid, createdby, taggedusers from "FOIRequestComments" frc   where commentid <> :commentid and parentcommentid = (select parentcommentid from "FOIRequestComments" frc   where commentid=:commentid) and isactive = true
                    ) cmt where commenttypeid =1"""
            rs = db.session.execute(text(sql), {'commentid': commentid})
            for row in rs:
                users.append({"commentid": row["commentid"], "createdby": row["createdby"], "taggedusers": row["taggedusers"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return users    
class FOIRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('commentid', 'ministryrequestid', 'parentcommentid','comment', 'commenttypeid','commenttype','isactive','created_at','createdby','updated_at','updatedby','taggedusers', 'parentcomment.taggedusers', 'commentsversion') 