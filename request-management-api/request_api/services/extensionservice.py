from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensionDocumentMappings import FOIRequestExtensionDocumentMapping
from request_api.services.requestservice import requestservice
from request_api.services.documentservice import documentservice
from request_api.services.extensionreasonservice import extensionreasonservice
from request_api.services.eventservice import eventservice
from request_api.services.events.extension import ExtensionType
from datetime import datetime
import asyncio
import json
import base64
from request_api.exceptions import BusinessException, Error

class extensionservice:
    """ FOI Extension management service
    """
    otherdateformat = '%Y-%m-%d'

    def getrequestextensions(self, requestid, version=None):
        extensions = []
        created_atdateformat = '%Y-%m-%d %H:%M:%S.%f'
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
                    "extendedduedate": self.__formatdate(entry["extendedduedate"], self.otherdateformat),  
                    "decisiondate": self.__formatdate(entry["decisiondate"], self.otherdateformat), 
                    "approvednoofdays": entry["approvednoofdays"], 
                    "created_at": self.__formatdate(entry["created_at"], created_atdateformat),  
                    "createdby": entry["createdby"]})        
        return extensions

    def __ispublicbodyextension(self, reasonid):
        extensionreason = extensionreasonservice().getextensionreasonbyid(reasonid)
        return 'extensiontype' in  extensionreason and extensionreason['extensiontype'] == ExtensionType.publicbody.value

    def getrequestextension(self, extensionid):
        requestextension = FOIRequestExtension().getextension(extensionid)
        extensiondocuments = self.__getextensiondocuments(requestextension["foirequestextensionid"], requestextension["version"])
        documents = self.__getextensiondocumentsinfo(extensiondocuments)
        extensionreason = extensionreasonservice().getextensionreasonbyid(requestextension['extensionreasonid'])
        requestextensionwithdocuments = self.__createextensionobject(requestextension, documents, extensionreason)
        return requestextensionwithdocuments

    def createrequestextension(self, foirequestid, ministryrequestid, extensionschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        reasonid = extensionschema['extensionreasonid']
        extensionreason = extensionreasonservice().getextensionreasonbyid(reasonid)
        ispublicbodyextension = self.__ispublicbodyextension(reasonid)
        if ('extensionstatusid' in extensionschema and extensionschema['extensionstatusid'] == 2) or ispublicbodyextension == True:
            self.validatecreateextension(ministryrequestid, extensionschema, ispublicbodyextension)
            ministryrequestschema = {
                "duedate": extensionschema['extendedduedate']
            }
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
            
            newduedate = \
            ministryrequestschema['duedate'] \
            if isinstance(ministryrequestschema['duedate'], str) \
            else self.__formatdate(ministryrequestschema['duedate'], self.otherdateformat)
           
            if result.success == True:
                version = self.__getversionforrequest(ministryrequestid)
                #Set isactive:false for extensions with previous ministry request version
                FOIRequestExtension.disableoldversions(version,ministryrequestid, userid)
                extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid, newduedate= newduedate)
        else:
            extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        if 'documents' in extensionschema and extensionschema['extensionstatusid'] != 1:
            self.saveextensiondocument(extensionschema['documents'], ministryrequestid, userid, extnsionresult.identifier)
        return extnsionresult
    

    def validatecreateextension(self, ministryrequestid, extensionschema, ispublicbodyextension= None):
        if ispublicbodyextension is None:
            ispublicbodyextension = self.__ispublicbodyextension(extensionschema['extensionreasonid'])
            
        if not ispublicbodyextension:
            return
        
        extensions = self.getrequestextensions(ministryrequestid)
        publicbodyextensiondays = [extension['extendedduedays'] for extension in extensions if extension['extensiontype'] == ExtensionType.publicbody.value]
        if sum(publicbodyextensiondays) + extensionschema['extendedduedays'] > 30:
            raise BusinessException(Error.INVALID_INPUT)
        
    def getextensiontobesaved(self, ministryrequestid, extensions,version):
        extensionstoadd=[]  
        extensionstodelete=[]
        extensionidstodelete=[]
        existingextensions = FOIRequestExtension.getextensions(ministryrequestid, version)    
        if(existingextensions is not None):  
            identifiersforexisting = []
            identifiersforaxis = []
            for existingextension in existingextensions:
                datestring = str(existingextension["extendedduedate"]).split(" ",1)[0]
                identifierforexisting= str(existingextension["extensionreasonid"])+datestring+str(existingextension["extensionstatusid"])   
                identifiersforexisting.append(identifierforexisting)
            for axisextension in extensions:
                datestring = str(axisextension["extendedduedate"]).split(" ",1)[0]
                identifierforaxis= str(axisextension["extensionreasonid"])+datestring+str(axisextension["extensionstatusid"])
                identifiersforaxis.append(identifierforaxis)
                if(identifierforaxis not in identifiersforexisting):
                    extensionstoadd.append(axisextension)
            for existingextension in existingextensions:
                datestring = str(existingextension["extendedduedate"]).split(" ",1)[0]
                identifierforexisting= str(existingextension["extensionreasonid"])+datestring+str(existingextension["extensionstatusid"])  
                if(identifierforexisting not in identifiersforaxis):
                    extensionstodelete.append(existingextension)
                    extensionidstodelete.append(existingextension["foirequestextensionid"])
        return extensionstoadd, extensionstodelete, extensionidstodelete
    
    def saveaxisrequestextension(self, ministryrequestid, extensions, userid, username):
        version = self.__getversionforrequest(ministryrequestid)
        extensionstoadd, extensionstodelete, extensionidstodelete = self.getextensiontobesaved(ministryrequestid, extensions,version)
        if(len(extensionstodelete) > 0):
            for existingextension in extensionstodelete:            
                self.deletedocuments(existingextension['foirequestextensionid'], existingextension['version'], ministryrequestid, userid) 
        deletedextensionresult= FOIRequestExtension.disableextensions(extensionidstodelete, userid)
        newextensions = []
        if(len(extensionstoadd) > 0):
            for extension in extensionstoadd:
                newextensions.append(self.__createextension(extension, ministryrequestid, version, userid))
        extnsionresult = FOIRequestExtension.saveextensions(newextensions)
        if deletedextensionresult.success == True and len(deletedextensionresult.args) > 0:
            # Post event for system generated comments & notifications for deleted extensions 
            eventservice().posteventforaxisextension(ministryrequestid, deletedextensionresult.args[0], userid, username, "delete")
        return extnsionresult

    def __createextension(self, extension, ministryrequestid, ministryrequestversion, userid): 
        createuserid = extension['createdby'] if 'createdby' in extension and extension['createdby'] is not None else userid
        createdat = extension['created_at'] if 'created_at' in extension  and extension['created_at'] is not None else datetime.now()
        approveddate = extension['approveddate'] if 'approveddate' in extension else None
        denieddate = extension['denieddate'] if 'denieddate' in extension else None
        decisiondate = approveddate if approveddate else denieddate
        approvednoofdays = extension['approvednoofdays'] if 'approvednoofdays' in extension else None

        if 'extensionstatusid' in extension:
            extensionstatusid = extension['extensionstatusid']
        else:
            extensionstatusid = 1        
      
        return FOIRequestExtension(
        extensionreasonid=extension['extensionreasonid'], 
        extendedduedays=extension['extendedduedays'], 
        extendedduedate=extension['extendedduedate'], 
        decisiondate=decisiondate, 
        approvednoofdays=approvednoofdays, 
        extensionstatusid=extensionstatusid, 
        version=1, 
        isactive=True, 
        foiministryrequest_id=ministryrequestid, 
        foiministryrequestversion_id=ministryrequestversion, 
        created_at=createdat, 
        createdby=createuserid)
     
    # This is used for edit/approve/deny extension
    # Edit can be normal edit like Pending -> Pending, Approved -> Approved, Denied -> Denied
    # or it can be complex edit like Pending -> Approved/Denied, Approved -> Pending/Denied, Denied -> Approved/Pending
    # if Pending -> Approved then the due date needs to be updated (new ministry version will get created), documents need to be mapped (if any)
    # if Approved -> Pending/Denied then, due date needs to be reverted back (new ministry version will get created), documents need to be deleted (if any)
    # any new ministry version created will create a new entry in FOIRequestExtensions, FOIMinistryDocuments (if any), FOIRequestExtensionDocumentsMapping (if any) tables
    def createrequestextensionversion(self, foirequestid, ministryrequestid, extensionid, extensionschema, userid, username):
        updatedduedate = None
        ministryversion = self.__getversionforrequest(ministryrequestid)
        extension = FOIRequestExtension.getextension(extensionid)
        extensionversion = extension['version']
        prevstatus = extension["extensionstatusid"]
        currentstatus = extensionschema["extensionstatusid"]
        isstatuschangedfromapproved = self.__isstatuschangedfromapproved(prevstatus, currentstatus)
        if isstatuschangedfromapproved == True:
            # gets the latest approved request
            approvedextension = self.getlatestapprovedrequest(extensionid, ministryrequestid, ministryversion)
            # gets the latest approved due date if any else gets the original due date
            updatedduedate = self.getlatestapprovedduedate(prevstatus, ministryrequestid, approvedextension)
       
        isdeletedocument = self.__isdeletedocument(isstatuschangedfromapproved, extensionid, extensionversion)
        if isdeletedocument == True:
            self.deletedocuments(extensionid, extensionversion, ministryrequestid, userid)  
       
        #copyextension has the updated extension with data passed from FE with the new version of extension       
        updatedextension = self.__copyextensionproperties(extension, extensionschema, extensionversion)
        # if current state is approved then gets the current extended due date
        extendedduedate = self.getextendedduedate(updatedextension)
 
        extensionresult = FOIRequestExtension.createextensionversion(ministryrequestid, ministryversion, updatedextension, userid)
        # Post event for system generated comments
        eventservice().posteventforextension(ministryrequestid, extensionid, userid, username, "modify")
        # save documents if it is part of current extension (update to the ministrydocuments table and extensiondocumentmapping table)
        if 'documents' in updatedextension and updatedextension['documents'] and updatedextension['extensionstatusid'] != 1:
            self.saveextensiondocument(updatedextension['documents'], ministryrequestid, userid, extensionid)
       
        # updates the duedate to extendedduedate or updatedduedate
        # new ministry, extension, extensionmapping and document version gets created
        if extensionresult.success == True and (isstatuschangedfromapproved == True or updatedextension['extensionstatusid'] == 2):
            ministryrequestschema = {
                "duedate": extendedduedate if extendedduedate else updatedduedate
            }
            requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
            version = self.__getversionforrequest(ministryrequestid)
            FOIRequestExtension.disableoldversions(version,ministryrequestid, userid)
            newduedate = \
            ministryrequestschema['duedate'] \
            if isinstance(ministryrequestschema['duedate'], str) \
            else self.__formatdate(ministryrequestschema['duedate'], self.otherdateformat)
            
            extensionresult.args = (*extensionresult.args, newduedate)
        return extensionresult
        
    def deleterequestextension(self, requestid, ministryrequestid, extensionid, userid):
        return self.createrequestextensionversionfordelete(requestid, ministryrequestid, extensionid, userid)

    # This is used for delete extension
    # soft delete of extension and related documents
    # due date reverted back to the prev approved due date
    def createrequestextensionversionfordelete(self, requestid, ministryrequestid, extensionid, userid):
        ministryversion = self.__getversionforrequest(ministryrequestid)
        extension = FOIRequestExtension.getextension(extensionid)
        prevstatus = extension["extensionstatusid"]
        extensionversion = extension['version']

        # this will be true if any document is attched to the extension
        isdeletedocument = self.__isdeletedocument(True, extensionid, extensionversion)

        # gets the latest approvedextension if any
        approvedextension = self.getlatestapprovedrequest(extensionid, ministryrequestid, ministryversion)
        # gets the latest approved due date if any else gets the original due date
        updatedduedate = self.getlatestapprovedduedate(prevstatus, ministryrequestid, approvedextension)

              
        #copyextension has the updated extension with soft delete(isactive: False) with the new version of extension       
        #updatedextension = self.__copyextensionproperties(extension, extensionschema, extensionversion)
        # this will create a new version of extension with isactive = False
        #extensionresult = FOIRequestExtension.createextensionversion(ministryrequestid, ministryversion, updatedextension, userid)
        #LATEST UPDATE :- updates existing isactive field to false if delete performed & no new version will be created for delete.
        extensionresult = FOIRequestExtension.disableextension(extension["foirequestextensionid"], userid)
        # once soft deleted, revert back the due date to prev due date
        # creates a new version of ministry request, extension, extensiondocuments(if any) and documents(if any)
        if extensionresult.success == True and prevstatus == 2:
            ministryrequestschema = {
                "duedate": updatedduedate
            }
            requestservice().saveministryrequestversion(ministryrequestschema, requestid, ministryrequestid, userid)
            version = self.__getversionforrequest(ministryrequestid)
            #Set isactive:false for extensions with previous ministry request version
            FOIRequestExtension.disableoldversions(version,ministryrequestid, userid)
            ## return due date
            
            newduedate = \
            ministryrequestschema['duedate'] \
            if isinstance(ministryrequestschema['duedate'], str) \
            else self.__formatdate(ministryrequestschema['duedate'], self.otherdateformat)
            
            extensionresult.args = (*extensionresult.args, newduedate)
        # soft delete the documents attached to the extension
        if extensionresult.success == True and isdeletedocument == True:
            self.deletedocuments(extensionid, extensionversion, ministryrequestid, userid)
            
        return extensionresult

    def __isstatuschangedfromapproved(self, prevstatus,  currentstatus):        
        if prevstatus == 2 and currentstatus != prevstatus:
            return True

    def getduedatetoupdate(self, extension, ministryrequestid, updatedextension, approvedextension):        
        # gets the latest approved due date if any else gets the original due date
        updatedduedate = self.getlatestapprovedduedate(extension, ministryrequestid, approvedextension)
        # if current state is approved then gets the current extended due date
        extendedduedate = self.getextendedduedate(updatedextension) 
        return extendedduedate if extendedduedate else updatedduedate

    def saveextensiondocument(self, extensiondocuments, ministryrequestid, userid, extensionid):
        documents = []        
        documentids = self.__savedocumentversion(ministryrequestid, extensiondocuments, userid)
        for documentid in documentids:
            documents.append(FOIMinistryRequestDocument().getdocument(documentid))      
        self.saveextensiondocumentversion(extensionid, documents, userid)

    def __isdeletedocument(self, isstatuschangedfromapproved, extensionid, extensionversion):
        isdeletedocument = False
        documents = self.__getextensiondocuments(extensionid, extensionversion)
        # 1. if prev status is Approved and current status is Pending or Denied
        # 2. Prev extension has documents
        # if any of the above condition is true then deletedocuments
        if isstatuschangedfromapproved == True or documents:
            isdeletedocument = True            
        return isdeletedocument

    def deletedocuments(self,extensionid, extensionversion, ministryrequestid, userid): 
        documents = self.__getextensiondocuments(extensionid, extensionversion)        
        for document in documents:
            documentservice().deleterequestdocument(ministryrequestid, document["foiministrydocumentid"], userid, "ministryrequest")
  
    def getextendedduedate(self, extensionschema):
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        # if status is Approved or reason is Public Body then directly take the extendedduedate
        if ('extensionstatusid' in extensionschema and extensionschema['extensionstatusid'] == 2) or extensionreason['extensiontype'] == ExtensionType.publicbody.value:
            return extensionschema['extendedduedate']

    def getlatestapprovedrequest(self, extensionid, ministryrequestid, ministryversion):
            return FOIRequestExtension().getlatestapprovedextension(extensionid, ministryrequestid, ministryversion)

    def getlatestapprovedduedate(self, prevstatus, ministryrequestid, approvedextension):       
        if approvedextension and len(approvedextension) != 0:  
            return approvedextension['extendedduedate']
        # if Prev extension status was Approved and no approved extension in FOIRequestExtension table then get the original DueDate from FOIMinisrtRequests table   
        elif prevstatus == 2 and not approvedextension:
            duedate = FOIMinistryRequest.getrequestoriginalduedate(ministryrequestid)
            return duedate
        #if current and prev status is Pending or Denied
        else:
            return None

    def saveextensiondocumentversion(self, extensionid, documents, userid):
        extensionversion = self.__getextensionversion(extensionid)
        if documents:
           return FOIRequestExtensionDocumentMapping.saveextensiondocument(extensionid, documents, extensionversion, userid)
        

    def __getextensionversion(self, extensionid):
        return FOIRequestExtension().getversionforextension(extensionid)

    def __createextensionobject(self, requestextension, documents, extensionreason):
        
        decisiondate =requestextension['decisiondate'] if 'decisiondate' in requestextension  else None
        approvednoofdays = requestextension['approvednoofdays'] if 'approvednoofdays' in requestextension  else None
        extension = {
            "foirequestextensionid": requestextension["foirequestextensionid"],
            "extensionreasonid": requestextension["extensionreasonid"],
            "extensionstatusid": requestextension["extensionstatusid"],
            "extendedduedays": requestextension["extendedduedays"],
            "extendedduedate": requestextension["extendedduedate"],
            "extensiontype": extensionreason["extensiontype"],           
            "approvednoofdays": approvednoofdays,
            "documents": documents
        }
        if requestextension["extensionstatusid"] == 2:
            extension["approveddate"] = decisiondate
        elif requestextension["extensionstatusid"] == 3:
            extension["denieddate"] = decisiondate
        return extension

    def __getextensiondocuments(self, extensionid, extensionversion):
        return FOIRequestExtensionDocumentMapping().getextensiondocuments(extensionid, extensionversion)

    def __getextensiondocumentsinfo(self, extensiondocuments):
        reqdocuments = []
        for extensiondocument in extensiondocuments:
            document = FOIMinistryRequestDocument().getdocument(extensiondocument["foiministrydocumentid"])
            if document["isactive"] == True:           
                reqdocuments.append({"foiministrydocumentid": document["foiministrydocumentid"], "filename": document["filename"], "documentpath": document["documentpath"], "category": document["category"]})
        return reqdocuments

    def __savedocumentversion(self, ministryrequestid, extensiondocumentschema, userid):
        documentids = []        
        for document in extensiondocumentschema:
            if 'foiministrydocumentid' in document:
                documentid = document['foiministrydocumentid']
            else:
                documentid = 0            
            documentresult = documentservice().createministrydocumentversion(ministryrequestid, documentid, document, userid)
            documentids.append(documentresult.identifier)
        return documentids

    def __copyextensionproperties(self, copyextension, extensionschema, version):
        copyextension['version'] = version +1
        copyextension['extensionreasonid'] = extensionschema['extensionreasonid'] if 'extensionreasonid' in extensionschema  else copyextension['extensionreasonid']   

        ispublicbodyextension = self.__ispublicbodyextension(copyextension['extensionreasonid'])
        if ispublicbodyextension == True:
            extensionstatusid = 2
        else:
            extensionstatusid = extensionschema['extensionstatusid'] if 'extensionstatusid' in extensionschema  else copyextension['extensionstatusid']
        copyextension['extensionstatusid'] = extensionstatusid
        copyextension['extendedduedays'] = extensionschema['extendedduedays'] if 'extendedduedays' in extensionschema  else copyextension['extendedduedays']
        copyextension['extendedduedate'] = extensionschema['extendedduedate'] if 'extendedduedate' in extensionschema  else copyextension['extendedduedate']
        approveddate = extensionschema['approveddate'] if 'approveddate' in extensionschema else copyextension['decisiondate']
        denieddate = extensionschema['denieddate'] if 'denieddate' in extensionschema else copyextension['decisiondate']
        decisiondate = approveddate if extensionstatusid == 2 else denieddate
        copyextension['decisiondate'] = decisiondate
        copyextension['approvednoofdays'] = extensionschema['approvednoofdays'] if 'approvednoofdays' in extensionschema  else copyextension['approvednoofdays']
        
        copyextension['documents'] = extensionschema['documents'] if 'documents' in extensionschema  else None
        copyextension['isactive'] =  extensionschema['isactive'] if 'isactive' in extensionschema  else True
        copyextension['created_at'] =  extensionschema['created_at'] if 'created_at' in extensionschema  else None
        copyextension['createdby'] = extensionschema['createdby'] if 'createdby' in extensionschema  else None
        return copyextension

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]

    def __formatdate(self, datevalue, format):        
        return datevalue.strftime(format) if datevalue is not None else None

    def getrequestextensionscount(self, requestid):
        extensionrecordscount = FOIRequestExtension.getextensionscount(requestid)
        return extensionrecordscount
        
  
