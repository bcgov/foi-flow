
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
from request_api import socketio
import asyncio
from request_api.utils.redispublisher import RedisPublisherService
class commentevent:
    """ FOI Event management service
    """
    def createcommentevent(self, commentid, requesttype, userid, isdelete=False, existingtaggedusers=False):
        try: 
            if isdelete == True:
               return self.__deletecommentnotification(commentid, userid)
            elif existingtaggedusers:
                return self.__editcommentnotification(commentid, requesttype, existingtaggedusers, userid)
            else:
                return self.__createcommentnotification(commentid, requesttype, userid)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Comment Notification Error', exception.message))
            return DefaultMethodResult(False,'Comment notifications failed',commentid)     

    def __createcommentnotification(self, commentid, requesttype, userid):
        _comment = self.__getcomment(commentid,requesttype)
        notificationservice().createcommentnotification(self.getcommentmessage(commentid, _comment), _comment, self.__getcommenttype(_comment), requesttype, userid)
        if _comment["taggedusers"] != '[]':
            notificationservice().createcommentnotification(self.getcommentmessage(commentid, _comment), _comment, "Tagged User Comments", requesttype, userid)    
        self.__pushcommentnotification(commentid)
        return DefaultMethodResult(True,'Comment notifications created',commentid)

    def __deletecommentnotification(self, commentid, userid):
        _pushnotifications = notificationservice().getcommentnotifications(commentid)
        for _pushnotification in _pushnotifications:  
            notificationservice().dismissnotification(userid, None, _pushnotification["idnumber"], _pushnotification["notificationuserid"])
            _pushnotification["action"] = "delete"
            RedisPublisherService().publishcommment(json.dumps(_pushnotification))
        return DefaultMethodResult(True,'Comment notifications deleted',commentid)      
    
    def __editcommentnotification(self, commentid, requesttype, existingtaggedusers, userid):
        _comment = self.__getcomment(commentid,requesttype)
        notificationservice().editcommentnotification(self.getcommentmessage(commentid, _comment), _comment, userid)
        newtaggedusers = [user for user in json.loads(_comment["taggedusers"]) if user not in json.loads(existingtaggedusers)]
        if newtaggedusers:
            _comment["taggedusers"] = json.dumps(newtaggedusers)
            notificationservice().createcommentnotification(self.getcommentmessage(commentid, _comment), _comment, "Tagged User Comments", requesttype, userid)    
        self.__pushcommentnotification(commentid)
        return DefaultMethodResult(True,'Comment notifications created',commentid)
    
    def __pushcommentnotification(self,commentid, _pushnotifications):
        try: 
            if os.getenv("SOCKETIO_MESSAGE_QTYPE") != "NONE":
                for _pushnotification in _pushnotifications:
                    if os.getenv("SOCKETIO_MESSAGE_QTYPE") == "REDIS":
                        RedisPublisherService().publishcommment(json.dumps(_pushnotification))
                    if os.getenv("SOCKETIO_MESSAGE_QTYPE") == "IN-MEMORY":
                        socketio.emit(_pushnotification["userid"], _pushnotification)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Comment Notification publish Error', exception.message))
            return DefaultMethodResult(False,'Comment notifications publish failed',commentid)  

    def __pushcommentnotification(self, commentid):
        _pushnotifications = notificationservice().getcommentnotifications(commentid)
        for _pushnotification in _pushnotifications:
            RedisPublisherService().publishcommment(json.dumps(_pushnotification))

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
        