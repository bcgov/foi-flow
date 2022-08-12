
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestFeeWaiver import FOIRequestFeeWaiver
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from datetime import datetime
import holidays
import maya
import os
from flask import current_app
from dateutil.parser import parse 

class feewaiverevent:
    """ Waiver Form Event management service

    """
    def createstatetransitionevent(self, requestid, userid, username):
        state = self.__haschanged(requestid)
        if state is not None:
            _commentresponse = self.__createcomment(requestid, state, userid, username)
            _notificationresponse = self.__createnotification(requestid, state, userid)
            if _commentresponse.success == True and _notificationresponse.success == True :
                return DefaultMethodResult(True,'Comment posted',requestid)
            else:   
                return DefaultMethodResult(False,'unable to post comment',requestid)
        return  DefaultMethodResult(True,'No change',requestid)
    
    def __createcomment(self, requestid, state, userid, username):
        comment = self.__preparecomment(requestid, state, username)
        return commentservice().createministryrequestcomment(comment, userid, 2)

    def __createnotification(self, requestid, state, userid):
        notification = self.__preparenotification(state)
        return notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "Fee Waiver Form", userid)

    def __preparecomment(self, requestid, state, username):
        comment = {"comment": self.__commentmessage(state, username)}
        comment['ministryrequestid']= requestid
        return comment
    
    def __preparenotification(self, state):
        return self.__notificationmessage(state)
        
    def __haschanged(self, requestid):
        status = FOIMinistryRequest.getrequeststatusById(requestid)
        if status[0]['requeststatusid'] != 11:
            return None
        else:
            states = FOIRequestFeeWaiver.getstatenavigation(requestid)        
            if len(states) == 2:
                newstate = states[0]
                oldstate = states[1]
                if newstate != oldstate and status:
                    return newstate
            return None    
    
    def __commentmessage(self, state, username):
        return  username+' updated Fee Waiver status to '+state

    def __notificationmessage(self, state):
        return  'Updated Fee Waiver Status to '+state 
