
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from request_api.models.FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser

import json
import base64
import maya
from request_api.auth import AuthHelper
from dateutil import tz, parser
from flask import jsonify
from datetime import datetime as datetime2

class dashboardeventservice:
    """ FOI Event Dashboard
    """
    
    def geteventqueuepagination(self, queuetype, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):
        _keyword, _filterfields = self.__validateandtransform(filterfields, keyword)
        notifications = None
        if AuthHelper.getusertype() == "iao" and (queuetype is None or queuetype == "all"):                                                                                           
                notifications = FOIRawRequestNotificationUser.geteventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, _keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager())
        elif  AuthHelper.getusertype() == "ministry" and (queuetype is not None and queuetype == "ministry"):
                notifications = FOIRequestNotificationUser.geteventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, _keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.isministryrestrictedfilemanager())
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
    
    def __validateandtransform(self, filterfields, keyword):
        _newvalue = keyword
        _newfilterfields = filterfields
        try:
            _newvalue = datetime2.strptime(keyword, '%d %b %Y').strftime('%y-%m-%d')
        except ValueError as ex:
            if "datetime" in _newfilterfields:
                _newfilterfields.remove("datetime")
        return _newvalue, _newfilterfields

    def __prepareevent(self, notification):
        return {
            'datetime' : maya.parse(notification.event_created_at).datetime(to_timezone='America/Vancouver', naive=False),
            'axisRequestId': notification.axisRequestId,
            'from': notification.createdby,            
            'to': notification.userid,
            'event': notification.event,
            'assignedGroup': notification.assignedGroup,
            'assignedTo': notification.assignedTo,            
            'assignedToFirstName':notification.assignedToFirstName,       
            'assignedToLastName':notification.assignedToLastName,  
            'assignedministrygroup': notification.assignedministrygroup,
            'assignedministryperson': notification.assignedministryperson,
            'assignedministrypersonFirstName':notification.assignedministrypersonFirstName,
            'assignedministrypersonLastName': notification.assignedministrypersonLastName

        }
