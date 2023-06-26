
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.commentservice import commentservice
from request_api.services.cfrfeeservice import cfrfeeservice
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

class cfrfeeformevent:
    """ CFR Form Event management service

    """
    def createstatetransitionevent(self, requestid, userid, username):
        cfrfee = cfrfeeservice().getcfrfee(requestid)
        state = self.__haschanged(requestid, cfrfee['cfrfeeid'])
        if state is not None:
            _commentresponse = self.__createcomment(requestid, state, userid, username)
            _notificationresponse = self.__createnotification(requestid, state, userid)
            if _commentresponse.success == True and _notificationresponse.success == True :
                return DefaultMethodResult(True,'Comment posted',requestid)
            else:   
                return DefaultMethodResult(False,'unable to post comment',requestid)
        return  DefaultMethodResult(True,'No change',requestid)


    def createeventforupdatedamounts(self, requestid, userid, username):
        feedata = FOIRequestCFRFee.getfeedataforamountcomparison(requestid)  
        updatedamounts={}
        _feewaivercommentresponse=DefaultMethodResult(True,'No change',requestid)
        _refundcommentresponse=DefaultMethodResult(True,'No change',requestid)
        if len(feedata) == 2:
            newfeedata = feedata[0]
            oldfeedata = feedata[1]
            newfeewaiveramount = self.__getvaluefromschema(newfeedata, "feewaiveramount")
            oldfeewaiveramount = self.__getvaluefromschema(oldfeedata, "feewaiveramount")
            if newfeewaiveramount != oldfeewaiveramount:
                updatedamounts = {'feewaiveramountchanged': newfeewaiveramount}
                _feewaivercommentresponse = self.__createcomment(requestid, None, userid, username, updatedamounts)
            newrefundamount = self.__getvaluefromschema(newfeedata, "refundamount")
            oldrefundamount = self.__getvaluefromschema(oldfeedata, "refundamount")
            if newrefundamount != oldrefundamount:
                updatedamounts = {'refundamountchanged': newrefundamount}
                _refundcommentresponse = self.__createcomment(requestid, None, userid, username, updatedamounts)
        return _feewaivercommentresponse, _refundcommentresponse

    def __createcomment(self, requestid, state, userid, username, updatedamounts=None):
        comment = self.__preparecomment(requestid, state, username, updatedamounts)
        return commentservice().createministryrequestcomment(comment, userid, 2)

    def __createnotification(self, requestid, state, userid):
        notification = self.__preparenotification(state)
        return notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "CFR Fee Form", userid)

    def __preparecomment(self, requestid, state, username, updatedamounts):
        comment = {"comment": self.__commentmessage(state, username, updatedamounts)}
        comment['ministryrequestid']= requestid
        return comment
    
    def __preparenotification(self, state):
        return self.__notificationmessage(state)
        
    def __haschanged(self, requestid, cfrfeeid):
        states = FOIRequestCFRFee.getstatenavigation(requestid, cfrfeeid)        
        if len(states) == 2:
            newstate = states[0]
            oldstate = states[1]
            if newstate != oldstate:
                return newstate
        elif len(states) == 1:
            return states[0]
        return None
    
    def __commentmessage(self, state, username, updatedamounts):
        if state is not None:
            return  username+' updated Fee Estimate status to '+state
        if updatedamounts is not None:
            if 'feewaiveramountchanged' in updatedamounts and updatedamounts['feewaiveramountchanged'] is not None:
                return username+ ' entered a fee waiver for the amount of $'+"{:.2f}".format(updatedamounts['feewaiveramountchanged'])
            if 'refundamountchanged' in updatedamounts and updatedamounts['refundamountchanged'] is not None:
                return username+ ' entered a refund for the amount of $'+"{:.2f}".format(updatedamounts['refundamountchanged'])
        

    def __notificationmessage(self, state):
        return  'Updated Fee Estimate Status to '+state 
    
    def __getvaluefromschema(self,requestsschema, property):
        return requestsschema.get(property) if property in requestsschema  else None 
