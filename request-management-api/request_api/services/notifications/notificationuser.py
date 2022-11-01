
from os import stat
from re import VERBOSE
import json
from request_api.services.watcherservice import watcherservice
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.services.notifications.notificationconfig import notificationconfig
from request_api.services.external.keycloakadminservice import KeycloakAdminService

class notificationuser:
    """ Notfication user service

    """
    
    def getnotificationusers(self, notificationtype, requesttype, userid, foirequest, foicomment=None, previousassignee=None):
        notificationusers = []
        if 'Assignment' in notificationtype:
            _users = self.__getassignees(foirequest, requesttype, notificationtype, previousassignee)
        elif 'Reply User Comments' in notificationtype:
            _users = self.__getcommentusers(foirequest, foicomment, requesttype)
        elif 'Tagged User Comments' in notificationtype:
            _users = self.__gettaggedusers(foicomment)
        elif 'Group Members' in notificationtype:
            _users = self.__getgroupmembers(foirequest["assignedministrygroup"])
        elif 'Watcher' in notificationtype:
            _users = self.__getwatchers(foirequest, requesttype, previousassignee)
        else:
            _users = self.__getassignees(foirequest, requesttype, notificationtype) + self.__getwatchers(foirequest, requesttype)
        for user in _users:
            if self.__isignorable(user, notificationusers, userid) == False and (("Tagged User Comments" not in notificationtype and self.__istaggeduser(user, foicomment, notificationtype) == False) or "Tagged User Comments" in notificationtype):
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
        
    def __getwatchers(self, foirequest, requesttype, previousassignee=None):
        notificationusers = []
        if previousassignee is not None:
            notificationusers.append({"userid": previousassignee, "usertype":notificationconfig().getnotificationusertypeid("Watcher")})
        else:
            if requesttype == "ministryrequest":
                watchers =  watcherservice().getallministryrequestwatchers(foirequest["foiministryrequestid"])
            else:
                watchers =  watcherservice().getrawrequestwatchers(foirequest['requestid'])
            for watcher in watchers:
                    notificationusers.append({"userid":watcher["watchedby"], "usertype":notificationconfig().getnotificationusertypeid("Watcher")})
        return notificationusers        
    
    def __getassignees(self, foirequest, requesttype, notificationtype, previousassignee=None):
        notificationusers = []
        notificationtypeid = notificationconfig().getnotificationusertypeid("Assignee")
        if previousassignee is not None:
            notificationusers.append({"userid": previousassignee, "usertype":notificationtypeid})
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
            taggedusers.append({"userid":entry["username"], "usertype":notificationconfig().getnotificationusertypeid("comment tagged user")})
        return taggedusers

    def __getgroupmembers(self,groupid):
        notificationusers = []
        notificationtypeid = notificationconfig().getnotificationusertypeid("Group Members")
        usergroupfromkeycloak= KeycloakAdminService().getmembersbygroupname(groupid) 
        for user in usergroupfromkeycloak[0].get("members"):
            notificationusers.append({"userid":user["username"], "usertype":notificationtypeid})
        return notificationusers 
        