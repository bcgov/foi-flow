
from os import stat
from re import VERBOSE

from notification_api.dao.models.FOIRequestComments import FOIRequestComment
from notification_api.dao.models.FOIMinistryRequest import FOIMinistryRequest

from notification_api.default_method_result import DefaultMethodResult
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import logging

class commentservice:
    """ FOI Comment management service
    """
    

    def createcomment(self, requesttype, requestid, comment, userid, type=1):
        foirequest = self.getrequest(requestid, requesttype) 
        _comment = self.__preparecomment(foirequest, comment)
        FOIRequestComment().savecomment(type, _comment, userid)
        return  DefaultMethodResult(True,'No change',requestid)

    def __preparecomment(self, foirequest, comment):
        _comment = FOIRequestComment()
        _comment.comment = comment["comment"]
        _comment.ministryrequestid = foirequest["foiministryrequestid"]
        _comment.version = foirequest["version"]
        _comment.taggedusers = None
        _comment.parentcommentid = None
        return _comment


    def getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequest(requestid)

