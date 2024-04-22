
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
    def createattachmentevent(self, ministryrequestid, userid, document):
        try:
            if 'rrt' in document['category']:
                #Create notification event for RRT document
                print(f"RRT Uploaded on FOI Request {ministryrequestid}")
                #message = f'RRT Uploaded on FOI Request {ministryrequestid}'
                message = self.notificationmessage('RRT', ministryrequestid)
                notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
                self.__createnotification(message, ministryrequestid, notificationtype, userid)
                self.__createcomment(ministryrequestid, message)
                return DefaultMethodResult(True, message, '')             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype, userid):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", notificationtype, userid)

    def __createcomment(self, ministryrequestid, message):
        if message is not None: 
            _comment = self.__preparecomment(ministryrequestid, message)
            return commentservice().createcomments(_comment, self.__defaultuserid(), 2)
    
    def __preparecomment(self, ministryrequestid, message):
        _comment = dict()
        _comment['comment'] = message
        _comment['ministryrequestid'] = ministryrequestid
        _comment['version'] = None
        _comment['taggedusers'] = None
        _comment['parentcommentid'] = None
        return _comment

    def notificationmessage(self, type, ministryrequestid):
        return f"{type} Attachment Uploaded on FOI Request {ministryrequestid}"

    def __notificationtype(self):
        return "Attachment Upload Event"
        
    def __defaultuserid(self):
        return "System"