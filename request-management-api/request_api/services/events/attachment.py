
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
    def createattachmentevent(self, requestid, userid, documents, requesttype):
        try:
            for document in documents:
                if 'rrt' in document['category']:
                    #Create notification event for RRT document
                    ministryversion = self.__getversionforrequest(requestid, requesttype)
                    message = self.notificationmessage('RRT', requestid)
                    notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
                    ret = self.__createnotification(message, requestid, notificationtype, userid, requesttype)
                    comment = self.__createcomment(requestid, message, ministryversion, userid, requesttype)
                    print('comment created')
                    return DefaultMethodResult(True, 'Attachment notification succedded', requestid) # ad the request id to the message             
            return DefaultMethodResult(True, 'No RTT attachment found' , requestid)             
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Attachment upload notification error', exception.message))
            return DefaultMethodResult(False,'Attachemnt notifications failed')     

    def __createnotification(self, message, requestid, notificationtype, userid, requesttype):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, requesttype , notificationtype, userid)

    def __createcomment(self, requestid, message, ministryversion, userid, requesttype):
        if message is not None:
            if requesttype == "ministryrequest":
                _comment = {"ministryrequestid": requestid, "version": ministryversion, "comment": message}        
                return commentservice().createcomments(_comment, userid, 2)
            else:
                _comment = {"requestid": requestid, "version": ministryversion, "comment": message}   
                return commentservice().createrawrequestcomment(_comment, userid, 2)
    
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