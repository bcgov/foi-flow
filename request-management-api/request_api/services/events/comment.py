
from os import stat
from re import VERBOSE
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRequestComments import FOIRequestComment
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

import asyncio
from request_api.utils.redispublisher import RedisPublisherService
class commentevent:
    """ FOI Event management service
    """
    def createcommentevent(self, commentid, requesttype, userid):
        try: 
            _comment = self.__getcomment(commentid,requesttype)
            notificationservice().createcommentnotification(self.getcommentmessage(commentid, _comment), _comment, self.__getcommenttype(_comment), requesttype, userid)
            if _comment["taggedusers"] != '[]':                
                notificationservice().createcommentnotification(self.getcommentmessage(commentid, _comment), _comment, "Tagged User Comments", requesttype, userid)    
            _pushnotifications = notificationservice().getcommentnotifications(commentid)
            for _pushnotification in _pushnotifications:
                asyncio.create_task(RedisPublisherService().publishcommment(json.dumps(_pushnotification)))
            return DefaultMethodResult(True,'Comment notifications created',commentid)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Comment Notification Error', exception.message))
            return DefaultMethodResult(False,'Comment notifications failed',commentid)     
        
    def getcommentmessage(self, commentid, comment):
        return {"commentid":commentid, "message" :self.__formatmessage(comment)}
    
    
  
    def __formatmessage(self, comment):
        _comment = json.loads(comment["comment"])
        msg = _comment["blocks"][0]["text"]
        if comment["taggedusers"] != '[]':
            msg = self.__formattaggedmessage(msg, json.loads(comment["taggedusers"]))
        msg = msg.strip()
        return msg
    
    def __formattaggedmessage(self, message, taggedusers):
        for _taguser in taggedusers:
            message = message.replace(_taguser["name"], "")    
        return message
        
    def __getcomment(self, commentid, requesttype):
        if requesttype == "ministryrequest":
            return FOIRequestComment.getcommentbyid(commentid)
        else:
            return FOIRawRequestComment.getcommentbyid(commentid)          
    
    def __getcommenttype(self, comment):
        if not comment["parentcommentid"]:
            return "New User Comments"
        else:
            return "Reply User Comments"
        