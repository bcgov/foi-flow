
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestOIPC import FOIRequestOIPC
from request_api.services.commentservice import commentservice
from request_api.services.oipcservice import oipcservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from dateutil.parser import parse
from request_api.utils.enums import CommentType

class oipcevent:
    """ FOI OIPC Event management service
    """
    
    def createoipcevent(self, requestid, userid):
        inquiryoutcomes = oipcservice().getinquiryoutcomes()
        version = FOIMinistryRequest.getversionforrequest(requestid)
        curoipcs = FOIRequestOIPC.getoipc(requestid, version)
        prevoipcs = FOIRequestOIPC.getoipc(requestid, version[0]-1)
        oipcsummary = self.__maintained(curoipcs, prevoipcs, inquiryoutcomes) 
        if oipcsummary is None or (oipcsummary and len(oipcsummary) <1):
            return  DefaultMethodResult(True,'No change',requestid)
        try:
            for oipc in oipcsummary:                  
                self.__createcomment(requestid, oipc, userid)
                self.__createnotification(requestid, oipc, userid)
            return DefaultMethodResult(True,'Comment posted',requestid)
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,requestid)   
                
        
    def __createcomment(self, requestid, oipc, userid):
        comment = {"ministryrequestid": requestid, "comment": self.__preparemessage(oipc)}        
        commentservice().createministryrequestcomment(comment, userid, CommentType.SystemGenerated.value)

    def __createnotification(self, requestid, oipc, userid):
        return notificationservice().createnotification({"message" : self.__preparemessage(oipc)}, requestid, "ministryrequest", "OIPC", userid, False)

    
    def __maintained(self,coipcs, poipcs, inquiryoutcomes):
        oipcs = []
        for coipc in coipcs:
            if self.__isoipcpresent(self.__getoipcnumber(coipc), poipcs) == False:
               oipcs.append(self.__createoipcsummary(coipc, EventType.add.value, inquiryoutcomes)) 
            else:
                if self.__isoutcomeclosed(coipc, poipcs) == True:
                    oipcs.append(self.__createoipcsummary(coipc, EventType.close.value, inquiryoutcomes))                  
                if self.__isinquirychanged(coipc, poipcs) == True:
                    oipcs.append(self.__createoipcsummary(coipc, EventType.inquirychange.value, inquiryoutcomes))                  
                elif self.__isinquiryoutcomechanged(coipc, poipcs, inquiryoutcomes) == True:
                    oipcs.append(self.__createoipcsummary(coipc, EventType.inquiryoutcome.value, inquiryoutcomes))                   
        return oipcs            
    
    # def __deleted(self, coipcs, poipcs):
    #     oipcs = []
    #     for poipc in poipcs:
    #         if self.__isoipcpresent(self.__getoipcnumber(poipc), coipcs) == False:      
    #             oipcs.append(self.__createoipcsummary(poipc, EventType.delete.value))   
    #     return oipcs      
    
    def __isoipcpresent(self, oipcno, poipcs):
        for oipc in poipcs:
            if self.__getoipcnumber(oipc) == oipcno:
                return True
        return False
    
    def __isoutcomeclosed(self, coipc, poipcs):
        for oipc in poipcs:
            if self.__getoipcnumber(oipc) == self.__getoipcnumber(coipc) and self.__getoutcome(oipc) != self.__getoutcome(coipc) and self.__getoutcome(coipc) == "Closed":
                return True
        return False

    def __isinquirychanged(self, coipc, poipcs):
        for oipc in poipcs:
            if self.__getoipcnumber(oipc) == self.__getoipcnumber(coipc) and self.__getinquiry(oipc) != self.__getinquiry(coipc):
                if self.__getinquirycomplydate(coipc) not in (None, "") and self.__getinquiryorderno(coipc) not in (None, "") and (self.__getinquiryorderno(oipc) != self.__getinquiryorderno(coipc) or self.__getinquirycomplydate(oipc) != self.__getinquirycomplydate(coipc)):
                    return True
        return False
    
    def __isinquiryoutcomechanged(self, coipc, poipcs, inquiryoutcomes):
        for oipc in poipcs:
            if self.__getoipcnumber(oipc) == self.__getoipcnumber(coipc) and self.__getinquiry(oipc) != self.__getinquiry(coipc):
                if self.__getinquiryoutcome(coipc, inquiryoutcomes) not in (None, "") and self.__getinquiryoutcome(oipc, inquiryoutcomes) != self.__getinquiryoutcome(coipc, inquiryoutcomes):
                    return True
        return False

    def __createoipcsummary(self, oipc, event, inquiryoutcomes):
        return {'oipcno': self.__getoipcnumber(oipc), 
        'reviewtype': self.__getoipcreviewtype(oipc), 
        'reason':self.__getreason(oipc),
        'outcome': self.__getoutcome(oipc),
        'inquirycomplydate': self.__getinquirycomplydate(oipc),
        'inquiryorderno': self.__getinquirycomplydate(oipc),
        'inquiryoutcome': self.__getinquiryoutcome(oipc, inquiryoutcomes),
        'event': event}
        
    def __getoipcnumber(self, dataschema):
        return dataschema['oipcno']

    def __getoipcreviewtype(self, dataschema):
        return dataschema['reviewtype.name']
    
    def __getreason(self, dataschema):
        return dataschema['reason.name']

    def __getoutcome(self, dataschema):
        return dataschema['outcome.name'] if dataschema['outcomeid'] not in (None,"") else None
    
    def __getinquirycomplydate(self, dataschema):
        return self.__getinquiry(dataschema)['inquirydate'] if dataschema['inquiryattributes'] not in (None,"") else None
    
    def __getinquiryoutcome(self, dataschema, inquiryoutcomes):
        if dataschema['inquiryattributes'] not in (None,""):
            inquiryoutcomeid = self.__getinquiry(dataschema)['inquiryoutcome']
            if inquiryoutcomeid not in (None,""):
                return self.__getinquiryoutcomename(inquiryoutcomeid, inquiryoutcomes)
        return None

    def __getinquiryorderno(self, dataschema):
        return self.__getinquiry(dataschema)['orderno'] if dataschema['inquiryattributes'] not in (None,"") else None
    
    def __getinquiry(self, dataschema):
        return dataschema['inquiryattributes']

    def __getinquiryoutcomename(self, inquiryoutcomeid, inquiryoutcomes):
        for outcome in inquiryoutcomes:
            if inquiryoutcomeid == outcome["inquiryoutcomeid"]:
                return outcome["name"]
        return None

    def __preparemessage(self, oipc):
        if oipc['event'] == EventType.add.value:
            return 'OIPC '+ oipc['reviewtype'] +' opened for '+ oipc['reason']
        elif oipc['event'] == EventType.close.value:
            return 'OIPC '+ oipc['reviewtype'] +' closed for '+ oipc['reason']
        elif oipc['event'] == EventType.inquirychange.value:
            _inquirychange_msg = 'OIPC Inquiry Order '+ oipc['inquiryorderno'] +' compliance date due '+oipc['inquirycomplydate']
            if oipc['inquiryoutcome'] not in (None, ""):
                return  _inquirychange_msg+' .Inquiry Decision:' + oipc['inquiryoutcome']
            else:
                return _inquirychange_msg
        elif oipc['event'] == EventType.inquiryoutcome.value:
            return 'OIPC '+ oipc['reviewtype'] +' Inquiry Decision: '+ oipc['inquiryoutcome']  
        
   
class EventType(Enum):
    add = "add"    
    delete = "delete"
    close = "close"
    inquirychange = "inquirychange"
    inquiryoutcome = "inquiryoutcome"
