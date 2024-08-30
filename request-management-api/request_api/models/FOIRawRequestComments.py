from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID, insert
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json


class FOIRawRequestComment(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestComments'
    # Defining the columns
    commentid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requestid = db.Column(
        db.Integer, db.ForeignKey('FOIRawRequests.requestid'))
    version = db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))
    comment = db.Column(db.Text, unique=False, nullable=True)
    taggedusers = db.Column(JSON, unique=False, nullable=True)
    parentcommentid = db.Column(db.Integer, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    commenttypeid = db.Column(db.Integer, unique=False, nullable=False)
    commentsversion = db.Column(db.Integer, nullable=False)
   
    @classmethod
    def savecomment(cls, commenttypeid, foirequestcomment, version, userid) -> DefaultMethodResult:
        commentsversion = 1
        parentcommentid = foirequestcomment["parentcommentid"] if 'parentcommentid' in foirequestcomment else None
        taggedusers = foirequestcomment["taggedusers"] if 'taggedusers' in foirequestcomment  else None
        newcomment = FOIRawRequestComment(commenttypeid=commenttypeid, requestid=foirequestcomment["requestid"], version=version, comment=foirequestcomment["comment"], parentcommentid=parentcommentid, isactive=True, createdby=userid,taggedusers=taggedusers, commentsversion=commentsversion)
        db.session.add(newcomment)
        db.session.commit()
        return DefaultMethodResult(True, 'Comment added', newcomment.commentid)

    @classmethod
    def disablecomment(cls, commentid, userid):
        dbquery = db.session.query(FOIRawRequestComment)
        comment = dbquery.filter_by(commentid=commentid)
        if(comment.count() > 0):
            childcomments = dbquery.filter_by(parentcommentid=commentid, isactive=True)
            if (childcomments.count() > 0) :
                return DefaultMethodResult(False,'Cannot delete parent comment with replies',commentid)
            comment.update({FOIRawRequestComment.isactive: False, FOIRawRequestComment.updatedby: userid,
                            FOIRawRequestComment.updated_at: datetime.now()}, synchronize_session=False)
            db.session.commit()
            return DefaultMethodResult(True, 'Comment disabled', commentid)
        else:
            return DefaultMethodResult(True, 'No Comment found', commentid)

    @classmethod
    def deactivatecomment(cls, commentid, userid, commentsversion):   
        dbquery = db.session.query(FOIRawRequestComment)
        comment = dbquery.filter_by(commentid=commentid, commentsversion=commentsversion)
        if(comment.count() > 0) :
            comment.update({FOIRawRequestComment.isactive: False, FOIRawRequestComment.updatedby: userid,
                            FOIRawRequestComment.updated_at: datetime.now()}, synchronize_session=False)
            db.session.commit()
            return DefaultMethodResult(True,'Comment deactivated',commentid)
        else:
            return DefaultMethodResult(True,'No Comment found',commentid) 
        
    @classmethod
    def updatecomment(cls, commentid, foirequestcomment, userid):
        dbquery = db.session.query(FOIRawRequestComment)
        comment = dbquery.filter_by(commentid=commentid).order_by(FOIRawRequestComment.commentsversion.desc()).first()
        _commentsversion = 0
        _existingtaggedusers = []
        _commenttypeid = None
        if comment is not None :
            _commenttypeid = comment.commenttypeid
            _existingtaggedusers = comment.taggedusers    
            _taggedusers = foirequestcomment["taggedusers"] if 'taggedusers' in foirequestcomment  else _existingtaggedusers        
            _commentsversion = int(comment.commentsversion)
            insertstmt = (
                insert(FOIRawRequestComment).
                values(
                    commentid= comment.commentid,
                    requestid=comment.requestid,
                    version=comment.version,
                    comment=foirequestcomment["comment"],
                    taggedusers=_taggedusers,
                    parentcommentid=comment.parentcommentid,
                    isactive=True,
                    created_at=datetime.now(),
                    createdby=userid,
                    updated_at=datetime.now(),
                    updatedby=userid,
                    commenttypeid= _commenttypeid, #foirequestcomment["commenttypeid"]
                    commentsversion=_commentsversion + 1
                )
            )
            updatestmt = insertstmt.on_conflict_do_update(index_elements=[FOIRawRequestComment.commentid, FOIRawRequestComment.commentsversion], 
                set_={"requestid": comment.requestid, "version":comment.version, "comment": foirequestcomment["comment"],
                      "taggedusers":_taggedusers, "parentcommentid":comment.parentcommentid,  "isactive":True, 
                      "created_at":datetime.now(), "createdby": userid, "updated_at": datetime.now(), "updatedby": userid, 
                      "commenttypeid": _commenttypeid
                      }
            )
            db.session.execute(updatestmt)
            db.session.commit()
            return DefaultMethodResult(True, 'Updated Comment added', commentid, _existingtaggedusers, _commentsversion, _commenttypeid)
        else:
            return DefaultMethodResult(True, 'No Comment found', commentid, _existingtaggedusers, _commentsversion, _commenttypeid)
        
    @classmethod
    def updatechildcomments(cls, parentcommentid, foirequestcomment, userid):   
        dbquery = db.session.query(FOIRawRequestComment)
        childcomments = dbquery.filter_by(parentcommentid=parentcommentid, isactive = True)     
        _existingtaggedusers = []
        _commentsversion = 0
        if childcomments is not None and childcomments.count() > 0:
            for comment in childcomments:
                _existingtaggedusers = comment.taggedusers
                _taggedusers = _existingtaggedusers
                _commentsversion = int(comment.commentsversion)
                insertstmt = (
                    insert(FOIRawRequestComment).
                    values(
                        commentid= comment.commentid,
                        requestid=comment.requestid,
                        version=comment.version,
                        comment=comment.comment,
                        taggedusers=_taggedusers,
                        parentcommentid=comment.parentcommentid,
                        isactive=True,
                        created_at=datetime.now(),
                        createdby=comment.userid,
                        updated_at=datetime.now(),
                        updatedby=userid,
                        commenttypeid= foirequestcomment["commenttypeid"], #comment.commenttypeid,
                        commentsversion=_commentsversion + 1
                    )
                )
                updatestmt = insertstmt.on_conflict_do_update(index_elements=[FOIRawRequestComment.commentid, FOIRawRequestComment.commentsversion], 
                    set_={"requestid": comment.requestid, "version":comment.version, "comment": comment.comment,
                          "taggedusers":_taggedusers, "parentcommentid":comment.parentcommentid,  "isactive":True, 
                          "created_at":datetime.now(), "createdby": comment.userid, "updated_at": datetime.now(), "updatedby": userid, 
                          "commenttypeid": foirequestcomment["commenttypeid"]
                         }
                )
                db.session.execute(updatestmt)
            db.session.commit()
            return DefaultMethodResult(True,'Updated Comment added',parentcommentid, _existingtaggedusers, _commentsversion, childcomments)
        else:
            return DefaultMethodResult(True,'No Comment found',parentcommentid, _existingtaggedusers, _commentsversion, None)
        
    @classmethod
    def deactivatechildcomments(cls, parentcommentid, userid, childcomments):   
        dbquery = db.session.query(FOIRawRequestComment)
        found = False
        for child in childcomments:
            comment = dbquery.filter_by(commentid=child.commentid, commentsversion=child.commentsversion, parentcommentid=parentcommentid)
            if(comment.count() > 0) :
                comment.update({FOIRawRequestComment.isactive:False, FOIRawRequestComment.updatedby:userid, FOIRawRequestComment.updated_at:datetime.now()}, synchronize_session = False)
                found = True
        if found:
            db.session.commit()
            return DefaultMethodResult(True, 'Reply Comments deactivated for parent', parentcommentid)
        else:
            return DefaultMethodResult(False, 'No Reply Comments found for parent', parentcommentid)

    @classmethod
    def getcomments(cls, requestid) -> DefaultMethodResult:
        comment_schema = FOIRawRequestCommentSchema(many=True)
        query = db.session.query(FOIRawRequestComment).filter_by(
            requestid=requestid, isactive=True).order_by(FOIRawRequestComment.commentid.asc()).all()
        return comment_schema.dump(query)

        # comments = []
        # try:
        #     sql = """SELECT distinct on (commentid) commentid, parentcommentid, requestid, version, comment, 
        #     created_at, createdby, updated_at, updatedby, isactive, commenttypeid, taggedusers, commentsversion
	    #     FROM public."FOIRawRequestComments" where requestid = :requestid and isactive = true order by commentid, commentsversion desc;"""
        #     rs = db.session.execute(text(sql), {'requestid': requestid})
        #     for row in rs:
        #         comments.append(dict(row))
        # except Exception as ex:
        #     logging.error(ex)
        #     raise ex
        # finally:
        #     db.session.close()
        # return comments
     
    
    @classmethod
    def getcommentbyid(cls, commentid) -> DefaultMethodResult:
        comment_schema = FOIRawRequestCommentSchema()
        query = db.session.query(FOIRawRequestComment).filter_by(
            commentid=commentid, isactive=True).first()
        return comment_schema.dump(query)


    @classmethod 
    def getcommentusers(cls, commentid):
        users = []
        try:
            sql = """select commentid, createdby, taggedusers from (
                    select commentid, commenttypeid, createdby, taggedusers from "FOIRawRequestComments" frc   where commentid = (select parentcommentid from "FOIRawRequestComments" frc   where commentid=:commentid) and isactive = true
                    union all 
                    select commentid, commenttypeid, createdby, taggedusers from "FOIRawRequestComments" frc   where commentid <> :commentid and parentcommentid = (select parentcommentid from "FOIRawRequestComments" frc   where commentid=:commentid) and isactive = true
                ) cmt where commenttypeid not in (2,3)"""
            rs = db.session.execute(text(sql), {'commentid': commentid})
            for row in rs:
                users.append({"commentid": row["commentid"], "createdby": row["createdby"], "taggedusers": row["taggedusers"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return users

class FOIRawRequestCommentSchema(ma.Schema):
    class Meta:
        fields = ('commentid', 'requestid', 'parentcommentid', 'comment', 'commenttypeid',
                  'commenttype', 'isactive', 'created_at', 'createdby', 'updated_at', 'updatedby','taggedusers', 'commentsversion')
