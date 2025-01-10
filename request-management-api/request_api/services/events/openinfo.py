from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.NotificationTypes import NotificationType
import json
from request_api.models.default_method_result import DefaultMethodResult

class openinfoevent:
    """ FOI Event management service

    """
    def createopeninfoevent(self, ministryrequestid, requestid, userid, username):
        _commentresponse = self.__createcomment(requestid, userid, username)
        _notificationresponse = self.__createnotification(requestid, userid)
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:
            return DefaultMethodResult(False,'unable to post comment',requestid)
    
    # def createopeninforequestevent(self, ministryrequestid, requestid, userid, username, requesttype):
    #     print("createopeninforequestevent called")
    #     print("========= : ",ministryrequestid, requestid, userid, username, requesttype)

    #     if requesttype == "EXEMPTION_REQUEST":
    #         return self.__handle_exemption_request(requestid, userid, username)
    #     elif requesttype == "EXEMPTION_APPROVED":
    #         return self.__handle_exemption_approved(requestid, userid, username, reason)
    #     elif requesttype == "EXEMPTION_DENIED":
    #         return self.__handle_exemption_denied(requestid, userid, username, reason)

    #     # _commentresponse = self.__createcomment(requestid, userid, username)
    #     # _notificationresponse = self.__createnotification(requestid, userid)
    #     if _commentresponse.success == True and _notificationresponse.success == True:
    #         return DefaultMethodResult(True,'Comment posted',requestid)
    #     else:
    #         return DefaultMethodResult(False,'unable to post comment',requestid)
    
    def handle_exemption_request(self, ministryrequestid, requestid, userid, username):
        print("handle_exemption_request called")
        print("========= ministryrequestid : ",ministryrequestid)
        print("========= requestid : ",requestid)
        print("========= userid : ",userid)
        print("========= username : ",username)
        print("================================================")

        try:        
            notificationtype = NotificationType().getnotificationtypeid("Exemption Request")
            print("========= notificationtype : ",notificationtype)
            if not notificationtype:
                print("Failed to get notification type ID")
                return DefaultMethodResult(False, 'Invalid notification type', requestid)

            notification_message = self.__notificationexemptionmessage(requestid, "EXEMPTION_REQUEST")
            if not notification_message:
                print("Failed to get notification message")
                return DefaultMethodResult(False, 'Invalid notification message', requestid)

            _notificationresponse = notificationservice().createnotification(
                {"message": notification_message},
                requestid,
                "ministryrequest",
                notificationtype,
                userid,
                False
            )
            # 4. Debug logging
            print(f"Notification parameters:")
            print(f"- message: {notification_message}")
            print(f"- ministryrequestid: {ministryrequestid}")
            print(f"- requestid: {requestid}")
            print(f"- notification_type: {notificationtype}")
            print(f"- userid: {userid}")

            if _notificationresponse.success:
                return DefaultMethodResult(True, 'notification posted', requestid)
            else:
                return DefaultMethodResult(False, 'Unable to post notification', requestid)  
        except Exception as e:
            print("========= error : ",e)
            return DefaultMethodResult(False, 'Unable to post notification', requestid)
    
    def dismiss_exemption_notifications(self, requestid):
        try:
            print("Dismissing exemption notifications for ministry request:", requestid)
            notificationservice().dismissnotifications_by_requestid_type(requestid, "ministryrequest", "Exemption Request")
            print("Successfully dismissed exemption notifications")
        
        except Exception as e:
            print("Error dismissing exemption notifications:", str(e))

    def __createcomment(self, requestid, userid, username):
        comment = self.__preparecomment(requestid, userid, username)
        return commentservice().createministryrequestcomment(comment, userid, 2)

    def __createtestnotification(self, requestid, userid):
        notification = self.__preparenotification(requestid)
        response = notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "fill in here", userid)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'Unable to post notification',requestid)

    def __notificationexemptionmessage(self, requestid, notificationtype):
        if notificationtype == "EXEMPTION_REQUEST":
            return "New Exemption Request is Received"
        elif notificationtype == "EXEMPTION_APPROVED":
            return "Exemption request approved"
        elif notificationtype == "EXEMPTION_DENIED":
            return "Exemption request denied. See Open Information tab for more information."
        return None  

    def __createnotification(self, requestid, userid):
        notification = self.__preparenotification(requestid)
        response = notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "fill in here", userid)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'Unable to post notification',requestid)

    def __preparenotification(self, requestid):
        return self.__notificationmessage(requestid)

    def __preparecomment(self, requestid, userid, username):
        comment = "fill in here"
        return comment

    def __notificationmessage(self, requestid):
        return "fill in here"
