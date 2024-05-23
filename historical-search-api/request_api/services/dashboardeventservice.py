
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from request_api.models.FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser
from request_api.models.FOIRequestNotificationDashboard import FOIRequestNotificationDashboard
from request_api.auth import AuthHelper
from dateutil import tz, parser
from flask import jsonify
from datetime import datetime as datetime2
from request_api.utils.commons.datetimehandler import datetimehandler
import re

class dashboardeventservice:
    """ FOI Event Dashboard
    """
    
    def geteventqueuepagination(self, queuetype, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):
        _filterfields = self.__validateandtransform(filterfields)
        notifications = None
        if AuthHelper.getusertype() == "iao" and (queuetype is None or queuetype == "all"):                                                                                           
                notifications = FOIRequestNotificationDashboard.getiaoeventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager())
        elif  AuthHelper.getusertype() == "ministry" and (queuetype is not None and queuetype == "ministry"):
                notifications = FOIRequestNotificationDashboard.getministryeventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.isministryrestrictedfilemanager())
        if notifications is not None:
            eventqueue = []
            for notification in notifications.items:
                eventqueue.append(self.__prepareevent(notification))

            meta = {
                'page': notifications.page,
                'pages': notifications.pages,
                'total': notifications.total,
                'prev_num': notifications.prev_num,
                'next_num': notifications.next_num,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev,
            }
            return jsonify({'data': eventqueue, 'meta': meta})
        return jsonify({'data': [], 'meta': None})
    
    def __validateandtransform(self, filterfields):
        return self.__transformfilteringfields(filterfields)
    
    def __transformfilteringfields(self, filterfields):
        return list(map(lambda x: x.replace('createdat', 'createdatformatted'), filterfields))

    

    def __prepareevent(self, notification):
        return {
            'id': notification.id+notification.crtid,
            'status': notification.status,
            'rawrequestid': notification.rawrequestid,
            'requestid': notification.requestid,
            'ministryrequestid': notification.ministryrequestid,
            'createdat' : notification.createdatformatted,
            #'createdat' : self.__formatedate(notification.createdat),
            'axisRequestId': notification.axisRequestId,
            'notification': notification.notification,
            'assignedToFormatted': notification.assignedToFormatted,
            'ministryAssignedToFormatted': notification.ministryAssignedToFormatted,
            'userFormatted': notification.userFormatted,
            'creatorFormatted': notification.creatorFormatted,
            'notificationType': notification.notificationtype,           
            'description':notification.description
        }

    