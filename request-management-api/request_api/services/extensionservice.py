from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.requestservice import requestservice
from request_api.services.extensionreasonservice import extensionreasonservice
import json
import base64

class extensionservice:
    """ FOI Extension management service
    """
    
    def getrequestextensions(self, requestid, version=None):
        extensions = []
        created_atdateformat = '%Y-%m-%d %H:%M:%S.%f'
        otherdateformat = '%Y-%m-%d'
        requestversion =  self.__getversionforrequest(requestid) if version is None else version
        extensionrecords = FOIRequestExtension.getextensions(requestid, requestversion)        
        for entry in extensionrecords:               
                extensions.append({"foirequestextensionid": entry["foirequestextensionid"], 
                    "extensionreasonid": entry["extensionreasonid"], 
                    "extensionreson": entry["reason"],
                    "extensiontype": entry["extensiontype"],
                    "extensionstatusid": entry["extensionstatusid"], 
                    "extensionstatus": entry["name"],
                    "extendedduedays": entry["extendedduedays"], 
                    "extendedduedate": self.__formatdate(entry["extendedduedate"], otherdateformat),  
                    "decisiondate": self.__formatdate(entry["decisiondate"], otherdateformat), 
                    "approvednoofdays": entry["approvednoofdays"], 
                    "created_at": self.__formatdate(entry["created_at"], created_atdateformat),  
                    "createdby": entry["createdby"]})        
        return extensions

    def createrequestextension(self, foirequestid, ministryrequestid, extensionschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        if 'extensiontype' in  extensionreason and extensionreason['extensiontype'] == 'Public Body':            
            ministryrequestschema = {
                "duedate": extensionschema['extendedduedate']
            }
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
           
            if result.success == True:
                version = self.__getversionforrequest(ministryrequestid)
                extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        else:
            extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        return extnsionresult

    def createrequestextensionversion(self, ministryrequestid, extensionid, extensionschema, userid):      
        version = self.__getversionforrequest(ministryrequestid)
        extension = FOIRequestExtension.getextension(extensionid)
        #save document here documentservice().createministryrequestdocument(ministryrequestid, extensionschema['document], userid)
        return FOIRequestExtension.createextensionversion(ministryrequestid, version, self.__copyextensionproperties(extension,extensionschema,extension['version']), userid)
    
    def __copyextensionproperties(self, extension, extensionschema, version):
        extension['version'] = version +1
        extension['extensionreasonid'] = extensionschema['extensionreasonid'] if 'extensionreasonid' in extensionschema  else extension['extensionreasonid']
        extension['extensionstatusid'] = extensionschema['extensionstatusid'] if 'extensionstatusid' in extensionschema  else extension['extensionstatusid']
        extension['extendedduedays'] = extensionschema['extendedduedays'] if 'extendedduedays' in extensionschema  else extension['extendedduedays']
        extension['extendedduedate'] = extensionschema['extendedduedate'] if 'extendedduedate' in extensionschema  else extension['extendedduedate']
        extension['decisiondate'] = extensionschema['decisiondate'] if 'decisiondate' in extensionschema  else extension['decisiondate']
        extension['approvednoofdays'] = extensionschema['approvednoofdays'] if 'approvednoofdays' in extensionschema  else extension['approvednoofdays']
        
        extension['document'] = extensionschema['document'] if 'document' in extensionschema  else None
        extension['isactive'] =  extensionschema['isactive'] if 'isactive' in extensionschema  else True
        extension['created_at'] =  extensionschema['created_at'] if 'created_at' in extensionschema  else None
        extension['createdby'] = extensionschema['createdby'] if 'createdby' in extensionschema  else None
        return extension

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]

    def __formatdate(self, datevalue, format):        
        formatteddate = datevalue.strftime(format) if datevalue is not None else None 
        return formatteddate
  