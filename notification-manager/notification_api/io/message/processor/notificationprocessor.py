import logging
from notification_api.services.notificationservice import notificationservice
from notification_api.services.commentservice import commentservice
from notification_api.services.external.keycloakadminservice import KeycloakAdminService
import json
from notification_api.default_method_result import DefaultMethodResult
from notification_api.io.message.schemas.notification import NotificationPublishSchema
class notificationprocessor:
    """ FOI notification processor
    """

    def handlemessage(self, message):
        notification = NotificationPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotification(notification)
        commentresp = self.__createcomment(notification)
        if commentresp.success == True and notificationresp.success == True:
            return DefaultMethodResult(True,'Comment posted',message["ministryrequestid"])
        else:   
            return DefaultMethodResult(False,'unable to post comment',message["ministryrequestid"])
  

    def __createnotification(self, notification):
        return notificationservice().createnotification("ministryrequest", notification.ministryrequestid, {"message": self.__notificationmessage(notification.createdby)}, "Records", notification.createdby )

    def __createcomment(self, notification):
        comment = {"comment": self.__commentmessage(notification.createdby)}     
        return commentservice().createcomment("ministryrequest", notification.ministryrequestid, comment, notification.createdby, 2)

    def __notificationmessage(self, username):
        return 'A batch of records has been uploaded by '+self.__formatname(username)

    def __commentmessage(self, username):
        return 'A batch of records has been uploaded by '+self.__formatname(username) 

    def __formatname(self, username):
        user = KeycloakAdminService().getuserbyidir(username)
        if  user["lastname"] is not None:
            return user["lastname"]+', '+user["firstname"]
        return user["firstname"]
         