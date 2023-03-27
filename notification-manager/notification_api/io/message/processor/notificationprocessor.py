import logging
from notification_api.services.notificationservice import notificationservice
from notification_api.services.commentservice import commentservice
from notification_api.services.external.keycloakadminservice import KeycloakAdminService
import json
from notification_api.default_method_result import DefaultMethodResult
from notification_api.io.message.schemas.notification import NotificationPublishSchema, NotificationHarmsPDFStitchPublishSchema
from config import DIVISION_PDF_STITCH_SERVICE_KEY

class notificationprocessor:
    """ FOI notification processor
    """

    def handlemessage(self, message):
        serviceid = message.get("serviceid")
        if serviceid == DIVISION_PDF_STITCH_SERVICE_KEY:
            return self.handlepdfstitchforharmsmessage(message)            
        else:
            return self.handlebatchmessage(message)
        
    def handlepdfstitchforharmsmessage(self, message):
        notification = NotificationHarmsPDFStitchPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotificationforharmspdfstitch(notification)
        commentresp = self.__createcommentforharmspdfstitch(notification)
        return self.__getmethodresult(message["ministryrequestid"], commentresp, notificationresp)
        
    def handlebatchmessage(self, message):
        notification = NotificationPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotification(notification)
        commentresp = self.__createcomment(notification)
        return self.__getmethodresult(message["ministryrequestid"], commentresp, notificationresp)
    
    def __getmethodresult(self, ministryid, commentresp, notificationresp):
        if commentresp.success == True and notificationresp.success == True:
            return DefaultMethodResult(True,'Comment/Notification posted',ministryid)
        else:   
            return DefaultMethodResult(False,'unable to post comment/notification',ministryid)

    def __createnotification(self, notification):
        return notificationservice().createnotification("ministryrequest", notification.ministryrequestid, {"message": self.__notificationmessage(notification.createdby)}, "Records", notification.createdby )

    def __createcomment(self, notification):
        comment = {"comment": self.__commentmessage(notification.createdby)}     
        return commentservice().createcomment("ministryrequest", notification.ministryrequestid, comment, notification.createdby, 2)

    def __notificationmessage(self, username):
        return 'A batch of records has been uploaded by '+self.__formatname(username)

    def __commentmessage(self, username):
        return 'A batch of records has been uploaded by '+self.__formatname(username)

    def __createnotificationforharmspdfstitch(self, notification):
        return notificationservice().createnotification("ministryrequest", notification.ministryrequestid, {"message": self.__createmessage(notification.errorflag)}, "PDFStitch", notification.createdby )

    def __createcommentforharmspdfstitch(self, notification):
        comment = {"comment": self.__createmessage(notification.errorflag)}     
        return commentservice().createcomment("ministryrequest", notification.ministryrequestid, comment, notification.createdby, 2)

    def __createmessage(self, errorflag):
        if errorflag == "YES":
            return 'Preparing records for harms export failed. Please Try Again'
        return 'Records for harms are ready for export'

    def __formatname(self, username):
        user = KeycloakAdminService().getuserbyidir(username)
        if  user["lastname"] is not None:
            return user["lastname"]+', '+user["firstname"]
        return user["firstname"]
         