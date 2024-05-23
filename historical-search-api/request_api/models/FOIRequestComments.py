from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID, insert
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
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
    def disablecomment(cls, commentid, userid):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0) :             
            childcomments = dbquery.filter_by(parentcommentid=commentid, isactive=True)
            if (childcomments.count() > 0) :
                return DefaultMethodResult(False,'Cannot delete parent comment with replies',commentid)
            comment.update({FOIRequestComment.isactive:False, FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment disabled',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid)  
    
    @classmethod
    def deactivatecomment(cls, commentid, userid, commentsversion):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid, commentsversion=commentsversion)
        if(comment.count() > 0) :
            comment.update({FOIRequestComment.isactive:False, FOIRequestComment.updatedby:userid, FOIRequestComment.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment deactivated',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid) 
        
    @classmethod
    def updatecomment(cls, commentid, foirequestcomment, userid):   
        dbquery = db.session.query(FOIRequestComment)
        comment = dbquery.filter_by(commentid=commentid).order_by(FOIRequestComment.commentsversion.desc()).first()        
        _existingtaggedusers = []
        _commentsversion = 0
        if comment is not None :            
            _existingtaggedusers = comment.taggedusers
            _taggedusers = foirequestcomment["taggedusers"] if 'taggedusers' in foirequestcomment  else _existingtaggedusers
            _commentsversion = int(comment.commentsversion)
            insertstmt = (
                insert(FOIRequestComment).
                values(
                    commentid=commentid,
                    ministryrequestid=comment.ministryrequestid,
                    version=comment.version,
                    comment=foirequestcomment["comment"],
                    taggedusers=_taggedusers,
                    parentcommentid=comment.parentcommentid,
                    isactive=True,
                    created_at=datetime2.now(),
                    createdby=userid,
                    updated_at=datetime2.now(),
                    updatedby=userid,
                    commenttypeid=comment.commenttypeid,
                    commentsversion=_commentsversion + 1
                )
            )
            updatestmt = insertstmt.on_conflict_do_update(index_elements=[FOIRequestComment.commentid, FOIRequestComment.commentsversion], 
                        set_={"ministryrequestid": comment.ministryrequestid,"version":comment.version, "comment": foirequestcomment["comment"],
                              "taggedusers":_taggedusers, "parentcommentid":comment.parentcommentid, "isactive":True,  
                              "created_at":datetime2.now(), "createdby": userid, "updated_at": datetime2.now(), "updatedby": userid, 
                              "commenttypeid": comment.commenttypeid 
                        }
            )
            db.session.execute(updatestmt)
            db.session.commit()
            return DefaultMethodResult(True,'Updated Comment added',commentid, _existingtaggedusers, _commentsversion)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid, _existingtaggedusers, _commentsversion)
            
    @classmethod
    def getcomments(cls, ministryrequestid)->DefaultMethodResult:   
        comment_schema = FOIRequestCommentSchema(many=True)
        query = db.session.query(FOIRequestComment).filter_by(ministryrequestid=ministryrequestid, isactive = True).order_by(FOIRequestComment.commentid.desc()).all()
        return comment_schema.dump(query)
        # comments = []
        # try:
        #     sql = """SELECT distinct on (commentid) commentid, parentcommentid, commentsversion, ministryrequestid, version, comment, created_at, createdby,
        #         updated_at, updatedby, isactive, commenttypeid, taggedusers
	    #         FROM public."FOIRequestComments" where ministryrequestid = :ministryrequestid and isactive = true order by commentid, commentsversion desc;"""
        #     rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
        #     for row in rs:
        #         # comments.append(
        #         #     {"commentid": row["commentid"], "parentcommentid": row["parentcommentid"], "commentsversion": row["commentsversion"], 
        #         #     "ministryrequestid": row["ministryrequestid"], "version": row["version"], "comment": row["comment"],
        #         #     "created_at": row["created_at"], "createdby": row["createdby"], "updated_at": row["updated_at"], "updatedby": row["updatedby"],
        #         #     "isactive": row["isactive"], "commenttypeid": row["commenttypeid"], "taggedusers": row["taggedusers"]
        #         #     }
        #         # )
        #         comments.append(dict(row))
        # except Exception as ex:
        #     logging.error(ex)
        #     raise ex
        # finally:
        #     db.session.close()
        # return comments
     
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