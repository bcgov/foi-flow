
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
    def createattachmentevent(self, ministryrequestid, document, userid, event):
        try:
            message = None
            notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
            print(f'#### The notification type is {notificationtype}')
            self.__createnotification(message, 'foiministryrequestid', notificationtype)
            return DefaultMethodResult(True, message, '')             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype):
        if message is not None: 
            return notificationservice().createremindernotification({"message" : message}, requestid, "ministryrequest", notificationtype, self.__defaultuserid())

    def notificationmessage(self, type):
        return f"{type} Attachment Uploaded"

    def __notificationtype(self):
        return "Attachment Upload Event"
        
    def __defaultuserid(self):
        return "System"