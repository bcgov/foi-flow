
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
            if keyword not in [None, ""] and len(filterfields) > 0:
                _newvalue = datetime2.strptime(keyword, '%Y %b %d').strftime('%y-%m-%d')
        except ValueError as ex:
            if "createdat" in _newfilterfields:
                _newfilterfields.remove("createdat")
        return _newvalue, _newfilterfields

    def __prepareevent(self, notification):
        return {
            'createdat' : maya.parse(notification.createdat).datetime(to_timezone='America/Vancouver', naive=False),
            'axisRequestId': notification.axisRequestId,
            'createdby': notification.createdby,            
            'to': notification.to,
            'notification': notification.notification,
            'assignedGroup': notification.assignedGroup,
            'assignedTo': notification.assignedTo,            
            'assignedToFirstName':notification.assignedToFirstName,       
            'assignedToLastName':notification.assignedToLastName,  
            'assignedministrygroup': notification.assignedministrygroup,
            'assignedministryperson': notification.assignedministryperson,
            'assignedministrypersonFirstName':notification.assignedministrypersonFirstName,
            'assignedministrypersonLastName': notification.assignedministrypersonLastName,
            'id': notification.id

        }