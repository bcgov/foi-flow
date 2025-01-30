
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.NotificationTypes import NotificationType
from request_api.models.default_method_result import DefaultMethodResult

class applicationfeeformevent:
    """ Application Form Event management service
    """
    def createfeestatuschangeevent(self, rawrequestid, requestid, ministryrequestid, data, userid, username):
        _commentresponse = self.__createfeestatuschangecomment(rawrequestid, requestid, ministryrequestid, data, userid, username)
        _notificationresponse = self.__createfeestatuschangenotification(rawrequestid, requestid, ministryrequestid, data, userid, username)
        if _commentresponse.success == True and _notificationresponse.success == True :
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:   
            return DefaultMethodResult(False,'unable to post comment',requestid)

    def createfeerefundevent(self, rawrequestid, requestid, ministryrequestid, refundamount, userid, username):
        _commentresponse = self.__createfeerefundcomment(rawrequestid, requestid, ministryrequestid, refundamount, userid, username)
        if _commentresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:   
            return DefaultMethodResult(False,'unable to post comment',requestid)

    def __createfeestatuschangecomment(self, rawrequestid, requestid, ministryrequestid, data, userid, username):
        comment = self.__preparefeestatuschangecomment(rawrequestid, requestid, ministryrequestid, data, userid, username)
        if ministryrequestid is not None:
            result = commentservice().createministryrequestcomment(comment, userid, 2)
        else:
            result = commentservice().createrawrequestcomment(comment, userid, 2)
        return result
    
    def __preparefeestatuschangecomment(self, rawrequestid, requestid, ministryrequestid, data, userid, username):
        if 'applicationfeestatus' in data and data['applicationfeestatus'].lower() == 'na-ige':
            appfeestatus = 'N/A - IGE'
        elif 'applicationfeestatus' in data and data['applicationfeestatus'].lower()   == 'paid':
            appfeestatus = 'Paid'
        elif 'applicationfeestatus' in data and data['applicationfeestatus'].lower()   == 'appfeeowing':
            appfeestatus = 'App Fee Owing'
        commentmessage = '{} has updated Application Fee Status to {}'.format(username, appfeestatus)
        if ministryrequestid is not None:
            comment = {"comment": commentmessage, "commenttypeid": 2, "ministryrequestid": ministryrequestid}
        else:
            comment = {"comment": commentmessage, "commenttypeid": 2, "requestid": rawrequestid}
        return comment
    
    def __createfeerefundcomment(self, rawrequestid, requestid, ministryrequestid, refundamount, userid, username):
        comment = self.__preparefeerefundcomment(rawrequestid, requestid, ministryrequestid, refundamount, username)
        if ministryrequestid is not None:
            result = commentservice().createministryrequestcomment(comment, userid, 2)
        else:
            result = commentservice().createrawrequestcomment(comment, userid, 2)
        return result

    def __preparefeerefundcomment(self, rawrequestid, requestid, ministryrequestid, refundamount, username):
        commentmessage = '{} has entered an application fee refund of ${}'.format(username, refundamount)
        if ministryrequestid is not None:
            comment = {"comment": commentmessage, "commenttypeid": 2, "ministryrequestid": ministryrequestid}
        else:
            comment = {"comment": commentmessage, "commenttypeid": 2, "requestid": rawrequestid}
        return comment

    def __createfeestatuschangenotification(self, rawrequestid, requestid, ministryrequestid, data, userid, username):
        notification = self.__preparefeestatuschangenotification(data['applicationfeestatus'])
        notificationtype = NotificationType().getnotificationtypeid("CFR Fee Form")
        if ministryrequestid is not None:
            requesttype = "ministryrequest"
            requestid = ministryrequestid
        else:
            requesttype = "rawrequest"
            requestid = rawrequestid
        return notificationservice().createnotification({"message" : notification}, requestid, requesttype, notificationtype, userid)

    def __preparefeestatuschangenotification(self, status):
        return self.__feestatusnotificationmessage(status)
    
    def __feestatusnotificationmessage(self, status):
        if status.lower() == 'na-ige':
            return 'Application Fee Status updated to N/A - IGE'
        elif status.lower() == 'paid':
            return 'Application Fee Status updated to Paid'
        elif status.lower() == 'appfeeowing':
            return 'Application Fee Status updated to App Fee Owing'
        else:
            return 'Application Fee Status updated to '+ status