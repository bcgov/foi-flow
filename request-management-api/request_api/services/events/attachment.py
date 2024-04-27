
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
    def createattachmentevent(self, ministryrequestid, userid, documents):
        try:
            for document in documents:
                if 'rrt' in document['category']:
                    #Create notification event for RRT document
                    ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
                    message = self.notificationmessage('RRT', ministryrequestid)
                    notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
                    self.__createnotification(message, ministryrequestid, notificationtype, userid)
                    self.__createcomment(ministryrequestid, message, ministryversion, userid)
                    return DefaultMethodResult(True, message, '')             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype, userid):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", notificationtype, userid)

    def __createcomment(self, ministryrequestid, message, ministryversion, userid):
        if message is not None: 
            _comment = self.__preparecomment(ministryrequestid, message, ministryversion)
            return commentservice().createcomments(_comment, userid, 2)
    
    def __preparecomment(self, ministryrequestid, message, ministryversion):
        _comment = dict()
        _comment['comment'] = message
        _comment['ministryrequestid'] = ministryrequestid
        _comment['version'] = ministryversion
        _comment['taggedusers'] = None
        _comment['parentcommentid'] = None
        return _comment

    def notificationmessage(self, type, ministryrequestid):
        return f"{type} Attachment Uploaded on FOI Request {ministryrequestid}"

    def __notificationtype(self):
        return "Attachment Upload Event"