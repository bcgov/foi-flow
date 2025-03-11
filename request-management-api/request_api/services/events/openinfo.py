from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.NotificationTypes import NotificationType
from request_api.models.OpenInformationStatuses import OpenInformationStatuses
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
import json
from request_api.models.default_method_result import DefaultMethodResult
from request_api.utils.enums import OpenInfoNotificationType
from request_api.models.OpenInformationExemptions import OpenInformationExemptions

class openinfoevent:
    """ FOI Event management service

    """
    def createopeninfoassigneeevent(self, ministryrequestid, requestid, userid, username, assigneedetails):
        comment = {"comment": '{0} assigned this request to {1}'.format(username,assigneedetails['assignedToName']), 'ministryrequestid': ministryrequestid}
        _commentresponse = commentservice().createministryrequestcomment(comment, userid, 2)
        notificationservice().dismissnotifications_by_requestid_type(requestid, "ministryrequest", OpenInfoNotificationType.OI_ASSIGNEE.value)
        _notificationtype = NotificationType.getnotificationtypeid(OpenInfoNotificationType.OI_ASSIGNEE.value)
        _notificationmessage = 'New Request Assigned to You.'
        _notificationresponse = self.__createnotification(requestid, userid, _notificationtype, _notificationmessage, {"oiassignedto": assigneedetails['assignedTo']})
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:
            return DefaultMethodResult(False,'unable to post comment',requestid)
    
    def createopeninfostateevent(self, ministryrequestid, requestid, userid, username):
        _openinfo = FOIOpenInformationRequests().getcurrentfoiopeninforequest(ministryrequestid)
        oistatuses = OpenInformationStatuses.getallstatuses()
        foirequest = notificationservice().getrequest(ministryrequestid, "ministryrequest")
        oistatus = None
        print(_openinfo)
        print(oistatuses)
        print("BANG")
        for status in oistatuses:
            if status['oistatusid'] == foirequest['oistatus_id']:
                oistatus = status['name']
        comment = {"comment": username + ' changed the state of the request to ' + (oistatus or "Unopened"), 'ministryrequestid': ministryrequestid}
        print("Comment", comment)
        _commentresponse = commentservice().createministryrequestcomment(comment, userid, 2)
        _notificationtype = NotificationType.getnotificationtypeid('OI State')
        print("_notificationtype", _notificationtype)
        _notificationmessage = "Moved to " + (oistatus or "Unopened") + " State"
        _notificationresponse = self.__createnotification(requestid, userid, _notificationtype, _notificationmessage, {"oiassignedto": _openinfo.get('oiassignedto')})
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:
            return DefaultMethodResult(False,'unable to post comment',requestid)
 
    def handle_exemption_request(self, ministryrequestid, requestid, userid, username, event_type, exemption_id=None):
        try:        
            notificationtype = NotificationType().getnotificationtypeid(event_type)
            if not notificationtype:
                return DefaultMethodResult(False, 'Invalid notification type', requestid)

            notification_message = self.__notificationexemptionmessage(requestid, event_type)
            if not notification_message:
                return DefaultMethodResult(False, 'Invalid notification message', requestid)

            _notificationresponse = notificationservice().createnotification(
                {"message": notification_message},
                requestid,
                "ministryrequest",
                notificationtype,
                userid,
                False
            )

            # Create comment for approval/denial
            if event_type in [OpenInfoNotificationType.EXEMPTION_APPROVED.value, OpenInfoNotificationType.EXEMPTION_DENIED.value]:
                _commentresponse = self.__createcomment(requestid, userid, username, event_type, exemption_id)
                if not _commentresponse.success:
                    return DefaultMethodResult(False, 'Unable to post comment', requestid)

            if _notificationresponse.success:
                return DefaultMethodResult(True, 'notification posted', requestid)
            else:
                return DefaultMethodResult(False, 'Unable to post notification', requestid)  
        except Exception as e:
            print("========= error : ",e)
            return DefaultMethodResult(False, 'Unable to post notification', requestid)
    
    def dismiss_exemption_notifications(self, requestid):
        try:
            notificationservice().dismissnotifications_by_requestid_type(requestid, "ministryrequest", OpenInfoNotificationType.EXEMPTION_REQUEST.value)
        except Exception as e:
            print("Error dismissing exemption notifications:", str(e))

    def __createcomment(self, requestid, userid, username, event_type, exemption_id):
        comment = self.__preparecomment(requestid, userid, username, event_type, exemption_id)
        data = {
            "ministryrequestid": requestid,
            "comment": comment
        }
        return commentservice().createministryrequestcomment(data, userid, 2)

    def __notificationexemptionmessage(self, requestid, notificationtype):
        if OpenInfoNotificationType.EXEMPTION_REQUEST.value == notificationtype:
            return "New Exemption Request is Received"
        elif OpenInfoNotificationType.EXEMPTION_APPROVED.value == notificationtype:
            return "Exemption request approved"
        elif OpenInfoNotificationType.EXEMPTION_DENIED.value == notificationtype:
            return "Exemption request denied. See Open Information tab for more information."
        return None  

    def __commentmessage(self, username, event_type, exemption_reason):
        if event_type == OpenInfoNotificationType.EXEMPTION_APPROVED.value:
            return f"Publication Exemption Approved by {username} for {exemption_reason}"
        elif event_type == OpenInfoNotificationType.EXEMPTION_DENIED.value:
            return f"Publication Exemption denied by {username}"
        return None

    def __createnotification(self, requestid, userid, type, message, requestjson):
        response = notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", type, userid, True, requestjson)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'Unable to post notification',requestid)

    def __preparenotification(self, requestid):
        return self.__notificationmessage(requestid)

    def __preparecomment(self, requestid, userid, username, event_type, exemption_id):
        if event_type in [OpenInfoNotificationType.EXEMPTION_APPROVED.value, OpenInfoNotificationType.EXEMPTION_DENIED.value]:
                exemption_reason = OpenInformationExemptions.getexemptionnamebyid(exemption_id)
                comment = self.__commentmessage(username, event_type, exemption_reason)
        return comment

    def __notificationmessage(self, requestid):
        return "fill in here"
