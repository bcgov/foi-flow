
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
        _keyword, _filterfields = self.__validateandtransform(filterfields, keyword)
        notifications = None
        if AuthHelper.getusertype() == "iao" and (queuetype is None or queuetype == "all"):                                                                                           
                notifications = FOIRequestNotificationDashboard.getiaoeventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, _keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager())
        elif  AuthHelper.getusertype() == "ministry" and (queuetype is not None and queuetype == "ministry"):
                notifications = FOIRequestNotificationDashboard.getministryeventpagination(groups, page, size, sortingitems, sortingorders, _filterfields, _keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.isministryrestrictedfilemanager())
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
        dtformats = ['%Y %b %d','%Y %b','%b %d','%d','%b','%Y']
        issupportedformat = False
        if keyword not in [None, ""] and len(filterfields) > 0:
            for dtformat in dtformats:  
                _newvalue, issupportedformat = self.__validatedateinput(_newvalue, dtformat)
                if issupportedformat == True:
                    _newvalue=_newvalue+'@'+dtformat
                    break
        if  (keyword in [None, ""] or issupportedformat == False) and "createdat" in _newfilterfields:
            _newfilterfields.remove("createdat")     
        return _newvalue, _newfilterfields

    def __validatedateinput(self, keyword, format):
        try:
            _toformat = self.__getdateformat(format)
            if _toformat is not None:
                newvalue = datetime2.strptime(keyword, format).strftime(_toformat)
            return newvalue, True
        except ValueError as ex:
            return keyword, False  

    def __getdateformat(self, format):
        """_summary_
        Supported Formats: 
        2023 Jun 15
        2023 Jun
        Jun 15
        2023
        Jun
        15     
        """
        if format == '%Y %b %d':
            return '%Y-%m-%d'
        elif format == '%Y %b':
            return '%Y-%m'
        elif format == '%b %d':
            return '%m-%d'
        elif format == '%d':
            return '%d'
        elif format == '%b':
            return '%m'
        elif format == '%Y':
            return '%Y'
        else:
            return None  

    def __prepareevent(self, notification):
        return {
            'id': self.__getid(notification),
            'status': notification.status,
            'rawrequestid': notification.rawrequestid,
            'requestid': notification.requestid,
            'ministryrequestid': notification.ministryrequestid,
            'idnumber': notification.idnumber,
            'createdat' : self.__formatedate(notification.createdat),
            'axisRequestId': notification.axisRequestId,
            'createdby': notification.createdby,      
            'userFirstName': notification.userFirstName,
            'userLastName': notification.userLastName,
            'to': notification.to,
            'creatorFirstName': notification.creatorFirstName,
            'creatorLastName': notification.creatorLastName,
            'notification': notification.notification,
            'assignedGroup': notification.assignedGroup,
            'assignedTo': notification.assignedTo,            
            'assignedToFirstName':notification.assignedToFirstName,       
            'assignedToLastName':notification.assignedToLastName,  
            'assignedministrygroup': notification.assignedministrygroup,
            'assignedministryperson': notification.assignedministryperson,
            'assignedministrypersonFirstName':notification.assignedministrypersonFirstName,
            'assignedministrypersonLastName': notification.assignedministrypersonLastName,
            'assignedToFormatted': notification.assignedToFormatted,
            'ministryAssignedToFormatted': notification.ministryAssignedToFormatted,
            'notificationType': notification.notificationtype,
            'userFormatted': notification.userFormatted,
            'creatorFormatted': notification.creatorFormatted,
            'description':notification.description
        }

    def __formatedate(self, input):
        return datetimehandler().convert_to_pst(input,'%Y %b %d | %I:%M %p')
    
    def __getid(self, notification):
        _id = notification.idnumber+str(notification.createdat)+notification.axisRequestId+notification.to+notification.createdby
        return re.sub(r"[^a-zA-Z0-9 ]", "", _id).replace(" ","")