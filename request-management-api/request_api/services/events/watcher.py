from cmath import asin
from os import stat
from re import VERBOSE
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
import json
from request_api.models.default_method_result import DefaultMethodResult
from request_api.utils.enums import CommentType

class watcherevent:

    def createwatcherevent(self, requestid, watcher, requesttype, userid, username):      
        #Create Notification - Watcher inactive   
        if watcher['isactive'] == False:
            notificationresponse = self.__createnotification(requesttype, watcher, userid, username)   
            if notificationresponse.success == True:
                return DefaultMethodResult(True,'Watcher Notification has been created',requestid)
            else:   
                return DefaultMethodResult(False,'unable to create notification for removed watcher',requestid) 
        else:
            #Dismiss Notification By ID & Userid - Watcher active
            notificationservice().dismissnotifications_by_requestid_type_userid(requestid, requesttype, 'Watcher', watcher['watchedby'])       
        return  DefaultMethodResult(True,'No change',requestid)

    def createwatchereventforrestricted(self, requestid, watcher, requesttype, userid, username):      
        #Create comment - add/remove Watcher
        #Create Notification - Watcher inactive
        if watcher['isactive'] == False:
            notificationresponse = self.__createnotification(requesttype, watcher, userid, username)
            commentrespose = self.__createcommentforremove(watcher['fullname'],username,requestid,userid,requesttype)
            if notificationresponse.success == True and commentrespose.success == True:
                return DefaultMethodResult(True,'Watcher Notification, Comment have been created',requestid)
            else:   
                return DefaultMethodResult(False,'unable to create notification and/or comment for removed watcher',requestid) 
        else:
            #Dismiss Notification By ID & Userid - Watcher active
            notificationservice().dismissnotifications_by_requestid_type_userid(requestid, requesttype, 'Watcher', watcher['watchedby'])
            commentrespose = self.__createcommentforadd(watcher['fullname'],username,requestid,userid,requesttype)
            if commentrespose.success == True:
                return DefaultMethodResult(True,'Watcher Comment has been created',requestid)
            else:
                return DefaultMethodResult(False,'unable to create comment for removed watcher',requestid)
        # return  DefaultMethodResult(True,'No change',requestid)


    def __createnotification(self, requesttype, watcher, userid, username):
        notification = self.__preparenotification(username)
        return notificationservice().createwatchernotification({"message" : notification}, requesttype, watcher, userid)

    def __preparenotification(self,username):
        return self.__notificationmessage(username)

    def __notificationmessage(self,username):
        return username+' has removed you as a watcher to this request'

    def __createcommentforadd(self, assigneename, username, requestid, userid, requesttype):
        _commentmessage ='{0} has made {1} a watcher'.format(username,assigneename)
        if requesttype == "ministryrequest":
            comment = {"ministryrequestid": requestid, "comment": _commentmessage}
            return commentservice().createministryrequestcomment(comment, userid, CommentType.SystemGenerated.value)
        else:
            comment = {"requestid": requestid, "comment": _commentmessage}
            return commentservice().createrawrequestcomment(comment, userid, CommentType.SystemGenerated.value)

    def __createcommentforremove(self, assigneename, username, requestid, userid, requesttype):
        _commentmessage ='{0} has removed {1} as a watcher'.format(username,assigneename)
        if requesttype == "ministryrequest":
            comment = {"ministryrequestid": requestid, "comment": _commentmessage}
            return commentservice().createministryrequestcomment(comment, userid, CommentType.SystemGenerated.value)
        else:
            comment = {"requestid": requestid, "comment": _commentmessage}
            return commentservice().createrawrequestcomment(comment, userid, CommentType.SystemGenerated.value)
