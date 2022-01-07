from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
import base64
import maya

class extensionservice:
    """ FOI Extension management service
    """
    
    def getrequestextensions(self, requestid, version=None):
        requestversion =  self.__getversionforrequest(requestid) if version is None else version
        extensions = FOIRequestExtension.getextension(requestid, requestversion)
        return self.__formatcreateddate(extensions)

    def createrequestextnesion(self, ministryrequestid, extensionschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        return FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, userid)
           

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