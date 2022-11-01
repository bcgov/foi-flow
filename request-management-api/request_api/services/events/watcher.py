from cmath import asin
from os import stat
from re import VERBOSE
from request_api.services.notificationservice import notificationservice
import json
from request_api.models.default_method_result import DefaultMethodResult

class watcherevent:

    def createwatcherevent(self, requestid, requesttype, userid,username,previousassignee, isactive):
        if(isactive == False):
            notificationresponse = self.__createnotification(requestid, requesttype, userid,username,previousassignee)   
            if notificationresponse.success == True:
                return DefaultMethodResult(True,'Watcher Notification has been created',requestid)
            else:   
                return DefaultMethodResult(False,'unable to create notification for removed watcher',requestid) 
        notificationservice().cleanupwatchernotifications(requestid, requesttype, "Watcher", previousassignee )       
        return  DefaultMethodResult(True,'No change',requestid)

    def __createnotification(self, requestid, requesttype, userid,username,previousassignee):
        notification = self.__preparenotification(username)
        return notificationservice().createnotification({"message" : notification}, requestid, requesttype, 'Watcher', userid, previousassignee)

    def __preparenotification(self,username):
        return self.__notificationmessage(username)

    def __notificationmessage(self,username):
        return username+' has removed you as a watcher to this request'        
            

        