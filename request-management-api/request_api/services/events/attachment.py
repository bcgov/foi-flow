
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.NotificationTypes import NotificationType
from request_api.exceptions import BusinessException
from request_api.models.default_method_result import DefaultMethodResult
from flask import current_app

class attachmentevent():
    """ FOI Attachment Event management service

    """
    def createattachmentevent(self, ministryrequestid, userid, documents, requesttype):
        try:
            for document in documents:
                if 'rrt' in document['category']:
                    #Create notification event for RRT document
                    ministryversion = self.__getversionforrequest(ministryrequestid, requesttype)
                    message = self.notificationmessage('RRT', ministryrequestid)
                    notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
                    ret = self.__createnotification(message, ministryrequestid, notificationtype, userid, requesttype)
                    comment = self.__createcomment(ministryrequestid, message, ministryversion, userid, requesttype)
                    return DefaultMethodResult(True, message, '')             
            return DefaultMethodResult(True, '' , '')             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype, userid, requesttype):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, requesttype , notificationtype, userid)

    def __createcomment(self, ministryrequestid, message, ministryversion, userid, requesttype):
        if message is not None: 
            _comment = self.__preparecomment(ministryrequestid, message, ministryversion)
            print("comment ", _comment)
            if requesttype == "ministryrequest":
                return commentservice().createcomments(_comment, userid, 2)
            else:
                return commentservice().createrawrequestcomment(_comment, userid, 2)
    
    def __preparecomment(self, ministryrequestid, message, ministryversion):
        _comment = dict()
        _comment['comment'] = message
        _comment['ministryrequestid'] = ministryrequestid
        _comment['requestid'] = ministryrequestid
        _comment['version'] = ministryversion
        _comment['taggedusers'] = None
        _comment['parentcommentid'] = None
        return _comment

    def notificationmessage(self, type, ministryrequestid):
        return f"{type} Attachment Uploaded on FOI Request {ministryrequestid}"

    def __notificationtype(self):
        return "Attachment Upload Event"
    
    def __getversionforrequest(self, requestid, requesttype):
        """ Returns the active version of the request id based on type.
        """
        if requesttype == "ministryrequest":
            document = FOIMinistryRequest.getversionforrequest(requestid)
        else:
            document = FOIRawRequest.getversionforrequest(requestid)
        if document:
            return document[0]