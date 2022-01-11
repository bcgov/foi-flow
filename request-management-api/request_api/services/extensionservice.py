from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.requestservice import requestservice
import json
import base64
import maya

class extensionservice:
    """ FOI Extension management service
    """
    
    def getrequestextensions(self, requestid, version=None):
        requestversion =  self.__getversionforrequest(requestid) if version is None else version
        extensions = FOIRequestExtension.getextensions(requestid, requestversion)
        return self.__formatcreateddate(extensions)

    def createrequestextension(self, foirequestid, ministryrequestid, extensionschema, userid):
        extnsionresult = {"success": False, "message": "", "identifier": 0}
        
        if extensionschema['extensionreasonid'] <= 4:            
            ministryrequestschema = {
                "duedate": extensionschema['extendedduedate']
            }
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)                      
            if result.success == True:
                version = self.__getversionforrequest(ministryrequestid)               
                extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, userid)               
        return extnsionresult
           

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]

    def __formatcreateddate(self, extensions):
        for extension in extensions:
            extension = self.__pstformat(extension)
        return extensions

    def __pstformat(self, extension):
        formatedcreateddate = maya.parse(extension['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        extension['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        return extension