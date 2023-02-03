
from os import stat
from re import VERBOSE
import json
from notification_api.dao.models.FOIRawRequest import FOIRawRequest
from notification_api.dao.models.FOIMinistryRequest import FOIMinistryRequest
from .notificationconfig import notificationconfig
from notification_api.services.external.keycloakadminservice import KeycloakAdminService

class notificationuser:
    """ Notfication user service

    """
    
    def getnotificationusers(self, notificationtype, requesttype, userid, foirequest, requestjson=None):
        notificationusers = []
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
        else:
            _users = self.__getassignees(foirequest, requesttype, notificationtype) + self.__getwatchers(notificationtype, foirequest, requesttype)
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
        if notificationtype == "Watcher":
            notificationusers.append({"userid": requestjson['watchedby'], "usertype":notificationconfig().getnotificationusertypeid("Watcher")})
        else:
            if requesttype == "ministryrequest":
                watchers =  FOIMinistryRequest().getwatchers(foirequest["foiministryrequestid"])
            else:
                watchers =  FOIRawRequest().getwatchers(foirequest['requestid'])
            for watcher in watchers:
                    notificationusers.append({"userid":watcher["watchedby"], "usertype":notificationconfig().getnotificationusertypeid("Watcher")})
        return notificationusers         
    
    def __getassignees(self, foirequest, requesttype, notificationtype, requestjson=None):
        notificationusers = []
        notificationtypeid = notificationconfig().getnotificationusertypeid("Assignee")
        if notificationtype == 'User Assignment Removal':
            notificationusers.append({"userid": requestjson['userid'], "usertype":notificationtypeid})
        else:
            if requesttype == "ministryrequest" and foirequest["assignedministryperson"] is not None and (notificationtype == 'Ministry Assignment' or 'Assignment' not in notificationtype):
                notificationusers.append({"userid":foirequest["assignedministryperson"], "usertype":notificationtypeid})
            if foirequest["assignedto"] is not None and foirequest["assignedto"] != '' and (notificationtype == 'IAO Assignment' or 'Assignment' not in notificationtype):
                notificationusers.append({"userid":foirequest["assignedto"], "usertype":notificationtypeid})
        return notificationusers          
    
    def __getcommentusers(self, foirequest, comment, requesttype):
        _requestusers = self.getnotificationusers("General", requesttype, "nouser", foirequest)
        commentusers = []
        commentusers.append({"userid":comment["createdby"], "usertype":self.__getcommentusertype(comment["createdby"],_requestusers)})
        taggedusers = self.__gettaggedusers(comment)
        if taggedusers is not None:
            commentusers.extend(taggedusers)
        if comment["parentcommentid"]:
            _commentusers = self.__getrelatedusers(comment, requesttype)
            for _commentuser in _commentusers:
                commentusers.append({"userid":_commentuser["createdby"], "usertype":self.__getcommentusertype(_commentuser["createdby"],_requestusers)})
                _skiptaguserforreplies = True
                if _skiptaguserforreplies == False:
                    taggedusers = self.__gettaggedusers(_commentuser)
                    if taggedusers is not None:
                        commentusers.extend(taggedusers)   
        return commentusers  
    
    def __getcommentusertype(self, userid, requestusers):
        for requestuser in requestusers:
            if requestuser["userid"] == userid:  
                return  requestuser["usertype"]   
        return notificationconfig().getnotificationusertypeid("comment user")
    
    def __getrelatedusers(self, comment, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest().getcommentusers(comment["commentid"])
        else:
            return FOIRawRequest().getcommentusers(comment["commentid"])
            
    def __gettaggedusers(self, comment): 
        if comment["taggedusers"] != '[]':
            return self.__preparetaggeduser(json.loads(comment["taggedusers"]))          
        return None   
    
    def __preparetaggeduser(self, data):
        taggedusers = [] 
        for entry in data:
            taggedusers.append({"userid":entry["username"], "usertype":notificationconfig().getnotificationusertypeid("comment tagged user")})
        return taggedusers

    def __getgroupmembers(self,groupid):
        notificationusers = []
        notificationtypeid = notificationconfig().getnotificationusertypeid("Group Members")
        usergroupfromkeycloak= KeycloakAdminService().getmembersbygroupname(groupid) 
        for user in usergroupfromkeycloak[0].get("members"):
            notificationusers.append({"userid":user["username"], "usertype":notificationtypeid})
        return notificationusers 
        