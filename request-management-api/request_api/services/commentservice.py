
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRawRequests import FOIRawRequest
import json
from dateutil.parser import *
import datetime 


class commentservice:
    """ FOI watcher management service

    """
    
    
    @classmethod    
    def createministryrequestcomment(self, data, userid):
        version = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])
        return FOIRequestComment.savecomment(1, data, version, userid) 

    @classmethod    
    def createrawrequestcomment(self, data, userid):
        version = FOIRawRequest.getversionforrequest(data["requestid"])
        return FOIRawRequestComment.savecomment(1, data, version, userid) 
    
    @classmethod    
    def disableministryrequestcomment(self, commentid, userid):
        return FOIRequestComment.disablecomment(commentid, userid) 

    @classmethod    
    def disablerawrequestcomment(self, commentid, userid):
        return FOIRawRequestComment.disablecomment(commentid, userid)     
        
    @classmethod    
    def updateministryrequestcomment(self, commentid, data, userid):
        return FOIRequestComment.updatecomment(commentid, data, userid) 

    @classmethod    
    def updaterawrequestcomment(self, commentid, data, userid):
        return FOIRawRequestComment.updatecomment(commentid, data, userid)          
        
    @classmethod    
    def getministryrequestcomments(self, ministryrequestid):
        data = FOIRequestComment.getcomments(ministryrequestid)
        return self.preparecomments(data)
    
    @classmethod    
    def getrawrequestcomments(self, requestid):
        data = FOIRawRequestComment.getcomments(requestid)
        return self.preparecomments(data)        
    
    @classmethod    
    def copyrequestcomment(self, ministryrequestid, comments, userid):
        _comments = []
        for comment in comments:
            response=FOIRequestComment.savecomment(comment['commentTypeId'], self.copyparentcomment(ministryrequestid, comment), 1, userid) 
            _comments.append({"ministrycommentid":response.identifier,"rawcommentid":comment['commentId']})
            if comment['replies']:
                for reply in comment['replies']:
                    response=FOIRequestComment.savecomment(reply['commentTypeId'], self.copyreplycomment(ministryrequestid, reply, response.identifier), 1, userid)      
                    _comments.append({"ministrycommentid":response.identifier,"rawcommentid":comment['commentId']})        
        return _comments
    
    @classmethod  
    def getmatchednministryid(self, _comments, parentid):
        for entry in _comments:
            if entry['rawcommentid'] == parentid:
                return  entry['ministrycommentid']      
        return None
    
    @classmethod  
    def copyparentcomment(self, ministryrequestid, entry):
        return {
            "ministryrequestid": ministryrequestid,
            "comment": entry['text']
            }
    
    @classmethod  
    def copyreplycomment(self, ministryrequestid, entry, parentcommentid):
        return {
            "ministryrequestid": ministryrequestid,
            "comment": entry['text'],
            "parentcommentid":parentcommentid
        }
    
    @classmethod  
    def preparecomments(self, data):
        comments=[]
        comments = self.parentcomments(data)
        for entry in data:
            if entry['parentcommentid'] is not None:
                for _comment in comments:
                    if entry['parentcommentid'] == _comment['commentId']:
                        _comment['replies'].append(self.comment(entry))            
        return comments        
    
    @classmethod    
    def parentcomments(self, data):
        parentcomments = []
        for entry in data:
            if entry['parentcommentid'] is None:
                _comment = self.comment(entry)
                _comment['replies'] = []
                parentcomments.append(_comment)        
        return parentcomments
          
        
    @classmethod    
    def comment(self, comment):
        return {
                "userId": comment['createdby'],
                "commentId": comment['commentid'],
                "text": comment['comment'],
                "date":  parse(comment["created_at"]).strftime('%Y-%m-%d %H:%M:%S.%f'),
                "parentCommentId":comment['parentcommentid'],
                "commentTypeId":comment['commenttypeid']
        }     