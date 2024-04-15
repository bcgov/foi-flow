
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.NotificationTypes import NotificationType
from request_api.exceptions import BusinessException
from request_api.models.default_method_result import DefaultMethodResult
from flask import current_app

class attachmentevent():
    """ FOI Attachment Event management service

    """
    def createattachmentevent(self, ministryrequestid, message, userid, event):
        try:
            notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
            self.__createnotification(message, ministryrequestid, notificationtype, userid)
            return DefaultMethodResult(True, message, '')             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype, userid):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", notificationtype, userid)

    def notificationmessage(self, type):
        return f"{type} Attachment Uploaded"

    def __notificationtype(self):
        return "Attachment Upload Event"
        
    def __defaultuserid(self):
        return "System"