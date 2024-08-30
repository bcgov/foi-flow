
from os import stat
from re import VERBOSE
import json
from request_api.services.watcherservice import watcherservice
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.services.notifications.notificationconfig import notificationconfig
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.services.commentservice import commentservice

class notificationuser:
    """ notification user service

    """
    
    def getnotificationusers(self, notificationtype, requesttype, userid, foirequest, requestjson=None):
        notificationusers = []
        print("Inside getnotificationusers - notificationtype:", notificationtype)
        if 'User Assignment Removal' == notificationtype:
            _users = self.__getassignees(foirequest, requesttype, notificationtype, requestjson)
        elif 'Assignment' in notificationtype:
            _users = self.__getassignees(foirequest, requesttype, notificationtype)
        elif 'Reply User Comments' in notificationtype:
            _users = self.__getcommentusers(foirequest, requestjson, requesttype)
        elif 'Tagged User Comments' in notificationtype:
            _users = self.__gettaggedusers(requestjson)
        elif 'Group Members' in notificationtype:
            _users = self.__getgroupmembers(foirequest["assignedministrygroup"])
        elif 'Watcher' in notificationtype:
            _users = self.__getwatchers(notificationtype, foirequest, requesttype, requestjson)
        elif 'Attachment Upload Event' in notificationtype:
            _users = self.__getgroupmembers('scanningteam') + self.__getassignees(foirequest, requesttype, notificationtype) + self.__getwatchers(notificationtype, foirequest, requesttype, requestjson)
        else:
            _users = self.__getassignees(foirequest, requesttype, notificationtype, requestjson) + self.__getwatchers(notificationtype, foirequest, requesttype, requestjson)
        for user in _users:
            if self.__isignorable(user, notificationusers, userid) == False and (("Tagged User Comments" not in notificationtype and self.__istaggeduser(user, requestjson, notificationtype) == False) or "Tagged User Comments" in notificationtype):
                notificationusers.append(user)
        return notificationusers    
    
    def __isignorable(self, notificationuser, users, userid):
        if notificationuser["userid"] == userid:
            return True
        else: 
            for user in users:
                if notificationuser["userid"] == user["userid"]:
                    return True
        return False     
     
    def __istaggeduser(self, notificationuser, foicomment, notificationtype):
        if "Comment" in notificationtype:
            _users = self.__gettaggedusers(foicomment)
            if _users is not None:
                for user in _users:
                    if notificationuser["userid"] == user["userid"]:
                        return True
        return False
        
    def __getwatchers(self, notificationtype, foirequest, requesttype, requestjson=None):
        notificationusers = []
        watchers = []
        if notificationtype == "Watcher":
            notificationusers.append({"userid": requestjson['watchedby'], "usertype":notificationconfig().getnotificationusertypelabel("Watcher")})
        else:
            isministryinternalcommenttype= self.__isministryinternalcomment(notificationtype,requestjson)
            isiaointernalcommenttype= self.__isiaointernalcomment(notificationtype,requestjson)
            if requesttype == "ministryrequest":
                watchers =  watcherservice().getallministryrequestwatchers(foirequest["foiministryrequestid"], isministryinternalcommenttype, 
                            isiaointernalcommenttype, self.__isministryonly(notificationtype))
            else:
                if isministryinternalcommenttype == False:
                    watchers =  watcherservice().getrawrequestwatchers(foirequest['requestid'])
            print("*****watchers:",watchers)
            for watcher in watchers:
                    notificationusers.append({"userid":watcher["watchedby"], "usertype":notificationconfig().getnotificationusertypelabel("Watcher")})
        return notificationusers         
    
    def __getassignees(self, foirequest, requesttype, notificationtype, requestjson=None):
        notificationusers = []
        notificationusertypelabel = notificationconfig().getnotificationusertypelabel("Assignee")
        if notificationtype == 'User Assignment Removal':
            notificationusers.append({"userid": requestjson['userid'], "usertype":notificationusertypelabel})
        else:
            if self.__isministryassigneeneeded(requesttype, foirequest, notificationtype, requestjson):
                notificationusers.append({"userid":foirequest["assignedministryperson"], "usertype":notificationusertypelabel})
            if self.__isfoiassigneeneeded(foirequest, notificationtype, requestjson):
                notificationusers.append({"userid":foirequest["assignedto"], "usertype":notificationusertypelabel})
        return notificationusers  
    

    def __isiaointernalcomment(self, notificationtype, requestjson):
        _iaointernaltype= commentservice().getcommenttypeidbyname("IAO Internal")
        _iaopeerreviewtype= commentservice().getcommenttypeidbyname("IAO Peer Review")
        if(notificationtype in ["New User Comments", "Reply User Comments", "Tagged User Comments", "General"] and 
            'commenttypeid' in requestjson and (requestjson['commenttypeid'] == _iaointernaltype or 
            requestjson['commenttypeid'] == _iaopeerreviewtype)):
                return True
        else:
            return False
        
    def __isministryinternalcomment(self, notificationtype, requestjson):
        ministryinternaltype= commentservice().getcommenttypeidbyname("Ministry Internal")
        ministrypeerreviewtype= commentservice().getcommenttypeidbyname("Ministry Peer Review")
        if(notificationtype in ["New User Comments", "Reply User Comments", "Tagged User Comments", "General"] and 
            'commenttypeid' in requestjson and (requestjson['commenttypeid'] == ministryinternaltype or 
            requestjson['commenttypeid'] == ministrypeerreviewtype)):
                return True
        else:
            return False
    

    def __isministryassigneeneeded(self, requesttype, foirequest, notificationtype, requestjson=None):
        if(requesttype == "ministryrequest" and foirequest["assignedministryperson"] is not None and (notificationtype == 'Ministry Assignment' or 'Assignment' not in notificationtype)):
            if ('Comments' in notificationtype or 'General' in notificationtype) and self.__isiaointernalcomment(notificationtype,requestjson):
                return False
            return True
        else:
            return False
        
    def __isfoiassigneeneeded(self, foirequest, notificationtype, requestjson=None):
        if self.__isministryonly(notificationtype) == False and foirequest["assignedto"] is not None and foirequest["assignedto"] != '' and (notificationtype == 'IAO Assignment' or 'Assignment' not in notificationtype):
            if ('Comments' in notificationtype or 'General' in notificationtype) and self.__isministryinternalcomment(notificationtype,requestjson):
                return False
            return True
        else:
            return False
    
    def __isministryonly(self, notificationtype):
        return True if notificationtype == "Division Due Reminder" else False 

    def __getcommentusers(self, foirequest, comment, requesttype):
        _requestusers = self.getnotificationusers("General", requesttype, "nouser", foirequest, comment)
        print("_requestusers:",_requestusers)
        commentusers = []
        commentusers.extend(_requestusers)
        taggedusers = self.__gettaggedusers(comment)
        if taggedusers is not None:
            commentusers.extend(taggedusers)
        if comment["parentcommentid"]:
            _commentusers = self.__getrelatedusers(comment, requesttype)
            for _commentuser in _commentusers:
                commentusers.append({"userid":_commentuser["createdby"], "usertype":self.__getcommentusertype(_commentuser["createdby"],_requestusers)})
                _skiptaguserforreplies = False
                if _skiptaguserforreplies == False:
                    taggedusers = self.__gettaggedusers(_commentuser)
                    if taggedusers is not None:
                        commentusers.extend(taggedusers)   
        return commentusers  
    
    def __getcommentusertype(self, userid, requestusers):
        for requestuser in requestusers:
            if requestuser["userid"] == userid:  
                return  requestuser["usertype"]   
        return notificationconfig().getnotificationusertypelabel("comment user")
    
    def __getrelatedusers(self, comment, requesttype):
        if requesttype == "ministryrequest":
            return FOIRequestComment.getcommentusers(comment["commentid"])
        else:
            return FOIRawRequestComment.getcommentusers(comment["commentid"])
            
    def __gettaggedusers(self, comment):
        if comment["taggedusers"] != '[]':
            return self.__preparetaggeduser(json.loads(comment["taggedusers"]))         
        return None   
    
    def __preparetaggeduser(self, data):
        taggedusers = [] 
        for entry in data:
            taggedusers.append({"userid":entry["username"], "usertype":notificationconfig().getnotificationusertypelabel("comment tagged user")})
        return taggedusers

    def __getgroupmembers(self,groupid):
        notificationusers = []
        notificationusertypelabel = notificationconfig().getnotificationusertypelabel("Group Members")
        usergroupfromkeycloak= KeycloakAdminService().getmembersbygroupname(groupid) 
        if usergroupfromkeycloak is not None and len(usergroupfromkeycloak) > 0:
            for user in usergroupfromkeycloak[0].get("members"):
                notificationusers.append({"userid":user["username"], "usertype":notificationusertypelabel})
            return notificationusers 
        return []