import logging
from notification_api.services.notificationservice import notificationservice
from notification_api.services.commentservice import commentservice
from notification_api.services.external.keycloakadminservice import KeycloakAdminService
import json
from notification_api.default_method_result import DefaultMethodResult
from notification_api.io.message.schemas.notification import (
    NotificationPublishSchema,
    NotificationHarmsPDFStitchPublishSchema,
    NotificationRedlineResponsePDFStitchPublishSchema,
)
from config import DIVISION_PDF_STITCH_SERVICE_KEY
from notification_api.util.enums import ServiceKey


class notificationprocessor:
    """FOI notification processor"""

    def handlemessage(self, message):
        serviceid = message.get("serviceid")
        if serviceid == ServiceKey.pdfstitchforhamrs.value.lower():
            return self.handlepdfstitchforharmsmessage(message)
        elif serviceid == ServiceKey.pdfstitchforredline.value.lower():
            return self.handlepdfstitchforredlinemessage(message)
        elif serviceid == ServiceKey.pdfstitchforresponsepackage.value.lower():
            return self.handlepdfstitchforresponsemessage(message)
        else:
            return self.handlebatchmessage(message)

    def handlepdfstitchforresponsemessage(self, message):
        notification = NotificationRedlineResponsePDFStitchPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotificationforresponse(notification)
        commentresp = self.__createcommentforresponse(notification)
        return self.__getmethodresult(
            message["ministryrequestid"], commentresp, notificationresp
        )

    def handlepdfstitchforredlinemessage(self, message):
        notification = NotificationRedlineResponsePDFStitchPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotificationforredline(notification)
        commentresp = self.__createcommentforredline(notification)
        return self.__getmethodresult(
            message["ministryrequestid"], commentresp, notificationresp
        )

    def handlepdfstitchforharmsmessage(self, message):
        notification = NotificationHarmsPDFStitchPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotificationforharmspdfstitch(notification)
        commentresp = self.__createcommentforharmspdfstitch(notification)
        return self.__getmethodresult(
            message["ministryrequestid"], commentresp, notificationresp
        )

    def handlebatchmessage(self, message):
        notification = NotificationPublishSchema()
        notification.__dict__.update(message)
        notificationresp = self.__createnotification(notification)
        commentresp = self.__createcomment(notification)
        return self.__getmethodresult(
            message["ministryrequestid"], commentresp, notificationresp
        )

    def __getmethodresult(self, ministryid, commentresp, notificationresp):
        if commentresp.success == True and notificationresp.success == True:
            return DefaultMethodResult(True, "Comment/Notification posted", ministryid)
        else:
            return DefaultMethodResult(
                False, "unable to post comment/notification", ministryid
            )

    def __createnotification(self, notification):
        return notificationservice().createnotification(
            "ministryrequest",
            notification.ministryrequestid,
            {"message": self.__notificationmessage(notification.createdby)},
            "Records",
            notification.createdby,
        )

    def __createcomment(self, notification):
        comment = {"comment": self.__commentmessage(notification.createdby)}
        return commentservice().createcomment(
            "ministryrequest",
            notification.ministryrequestid,
            comment,
            notification.createdby,
            2,
            notification.__dict__.get('createdat')
        )

    def __notificationmessage(self, username):
        return "A batch of records has been uploaded by " + self.__formatname(username)

    def __commentmessage(self, username):
        return "A batch of records has been uploaded by " + self.__formatname(username)

    def __createnotificationforharmspdfstitch(self, notification):
        return notificationservice().createnotification(
            "ministryrequest",
            notification.ministryrequestid,
            {
                "message": self.__createmessage(
                    notification.errorflag,
                    notification.totalskippedfilecount,
                    notification.totalskippedfiles,
                )
            },
            "PDFStitch",
            notification.createdby,
        )

    def __createcommentforharmspdfstitch(self, notification):
        comment = {
            "comment": self.__createmessage(
                notification.errorflag,
                notification.totalskippedfilecount,
                notification.totalskippedfiles,
            )
        }
        return commentservice().createcomment(
            "ministryrequest",
            notification.ministryrequestid,
            comment,
            notification.createdby,
            2,
        )

    def __createnotificationforresponse(self, notification):
        return notificationservice().createnotification(
            "ministryrequest",
            notification.ministryrequestid,
            {"message": self.__createresponsemessage(notification.errorflag)},
            "PDFStitch",
            notification.createdby,
        )

    def __createcommentforresponse(self, notification):
        if notification.feeoverridereason is not None and notification.feeoverridereason != '':
            comment = {"comment": notification.feeoverridereason}
            commentservice().createcomment(
                "ministryrequest",
                notification.ministryrequestid,
                comment,
                notification.createdby,
                2,
            )
        comment = {"comment": self.__createresponsemessage(notification.errorflag)}
        return commentservice().createcomment(
            "ministryrequest",
            notification.ministryrequestid,
            comment,
            notification.createdby,
            2,
        )

    def __createnotificationforredline(self, notification):
        return notificationservice().createnotification(
            "ministryrequest",
            notification.ministryrequestid,
            {"message": self.__createredlinemessage(notification.errorflag)},
            "PDFStitch",
            notification.createdby,
        )

    def __createcommentforredline(self, notification):
        comment = {"comment": self.__createredlinemessage(notification.errorflag)}
        return commentservice().createcomment(
            "ministryrequest",
            notification.ministryrequestid,
            comment,
            notification.createdby,
            2,
        )
    
    def __createresponsemessage(self, errorflag):
        if errorflag == "YES":
            return "Creating the Release Package failed. Please try again"
        return "Release Package ready for download"

    def __createredlinemessage(self, errorflag):
        if errorflag == "YES":
            return "Creating the redlines for sign off failed. Please try again"
        return "Redlines for sign off ready for download"

    def __createmessage(self, errorflag, totalskippedfilecount, totalskippedfiles):
        if int(totalskippedfilecount) > 0:
            totalskippedfiles = json.loads(totalskippedfiles)
            files = ", ".join(file for file in totalskippedfiles)
            message = (
                files
                + " file(s) could not be added to package, please check record for errors"
            )
            return message
        elif errorflag == "YES":
            return "Preparing records for harms export failed. Please Try Again"
        return "Records for harms are ready for export"

    def __formatname(self, username):
        user = KeycloakAdminService().getuserbyidir(username)
        if user["lastname"] is not None:
            return user["lastname"] + ", " + user["firstname"]
        return user["firstname"]
