from datetime import datetime
from notification_api.dao.db import getconnection
import logging
from marshmallow import EXCLUDE, Schema, fields, validate
import json


class FOIRequestComment(object):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE
    commentid = fields.Int(data_key="commentid") 
    ministryrequestid = fields.Int(data_key="ministryrequestid") 
    version = fields.Int(data_key="version") 
    comment = fields.Str(data_key="comment")
    taggedusers = fields.Str(data_key="taggedusers")
    parentcommentid = fields.Int(data_key="parentcommentid") 
    isactive = fields.Boolean(data_key="isactive")
    createdby = fields.Str(data_key="createdby")
    created_at = fields.Str(data_key="created_at")
    commenttypeid = fields.Int(data_key="commenttypeid") 

    
    @classmethod
    def savecomment(cls, commenttypeid, foirequestcomment, userid): 
        try:
            id_of_new_row = None
            data = foirequestcomment.__dict__
            parentcommentid = data["parentcommentid"] if data["parentcommentid"] is not None else None
            taggedusers = str(data["taggedusers"]) if data["taggedusers"] is not None  else None
            
            conn = getconnection()
            cursor = conn.cursor()
           
            cursor.execute('INSERT INTO public."FOIRequestComments" (parentcommentid, ministryrequestid, "version", commenttypeid, \
                                comment, taggedusers, isactive, createdby, created_at) \
                                VALUES(%s::integer,%s::integer, %s::integer, %s::integer,%s,%s,%s::boolean,%s,%s) RETURNING commentid', 
                                (parentcommentid, int(data["ministryrequestid"]), int(data["version"]), commenttypeid,
                                    str(data["comment"]), taggedusers, True, userid, datetime.now()))
            conn.commit()
            id_of_new_row = cursor.fetchone()[0]
            cursor.close()
            return id_of_new_row            
        except(Exception) as error:
            logging.error(error)
            raise   
        finally:
            conn.close()

    