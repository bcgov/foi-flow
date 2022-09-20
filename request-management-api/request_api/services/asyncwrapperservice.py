
import os

import asyncio
from request_api.utils.redispublisher import RedisPublisherService
from request_api.services.eventservice import eventservice

enable_async = False if os.getenv('DEBUG_MODE') == "ON" else True

class asyncwrapperservice:


    def publishrequest(self, json_data):
        redispubservice = RedisPublisherService()
        if enable_async == True:
            asyncio.ensure_future(redispubservice.publishrequest(json_data))
        else:
            print("to do")
            print(json_data)
            redispubservice.publishrequestsync(json_data)
            
    def postevent(self, requestid, requesttype, userid, username, isministryuser):
        if enable_async == True:
            asyncio.ensure_future(eventservice().postevent(requestid, requesttype, userid, username, isministryuser))
        else:
            eventservice().posteventsync(requestid, requesttype, userid, username, isministryuser)

    def postpaymentevent(self, ministry_request_id):
        if enable_async == True:
            asyncio.ensure_future(eventservice().postpaymentevent(ministry_request_id))
        else:
            eventservice().postpaymenteventsync(ministry_request_id)

    def posteventforcfrfeeform(self, ministryrequestid, userid, username):
        if enable_async == True:
            asyncio.ensure_future(eventservice().posteventforcfrfeeform(ministryrequestid, userid, username))
        else:
            eventservice().posteventforcfrfeeformsync(ministryrequestid, userid, username)

    def postcommentevent(self, commentid, requesttype, userid, isdelete=False):
        if enable_async == True:
            asyncio.ensure_future(eventservice().postcommentevent(commentid, requesttype, userid, isdelete))
        else:
            eventservice().postcommenteventsync(commentid, requesttype, userid, isdelete)