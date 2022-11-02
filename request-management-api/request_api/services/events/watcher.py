from cmath import asin
from os import stat
from re import VERBOSE
from request_api.services.notificationservice import notificationservice
import json
from request_api.models.default_method_result import DefaultMethodResult

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

    
    def __createnotification(self, requesttype, watcher, userid, username):
        notification = self.__preparenotification(username)
        return notificationservice().createwatchernotification({"message" : notification}, requesttype, watcher, userid)

    def __preparenotification(self,username):
        return self.__notificationmessage(username)

    def __notificationmessage(self,username):
        return username+' has removed you as a watcher to this request'        
            

        