from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
from request_api.models.FOIApplicantCorrespondenceAttachments import FOIApplicantCorrespondenceAttachment
from request_api.models.FOIApplicantCorrespondenceResponses import FOIApplicantCorrespondenceResponse
from request_api.models.FOIApplicantCorrespondenceEmails import FOIApplicantCorrespondenceEmail
from request_api.models.FOIApplicantCorrespondencesRawRequests import FOIApplicantCorrespondenceRawRequest
from request_api.models.FOIApplicantCorrespondenceEmailsRawRequests import FOIApplicantCorrespondenceEmailRawRequest
from request_api.models.FOIApplicantCorrespondenceAttachmentsRawRequests import FOIApplicantCorrespondenceAttachmentRawRequest

from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest

import maya
import json
import html
from datetime import datetime
class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active applicant correspondence templates
        """
        templates = ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()
        for template in templates:
            template["created_at"] = self.__pstformat(template['created_at'])
        return templates
    
    def gettemplatebyid(self, templateid):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.get_template_by_id(templateid)

    def getapplicantcorrespondencelogs(self,ministryrequestid, rawrequestid):
        """ Returns the active applicant correspondence logs
        """
        _correspondencelogs = FOIApplicantCorrespondenceRawRequest.getapplicantcorrespondencesrawrequests(rawrequestid)
        _correspondenceattachments = FOIApplicantCorrespondenceAttachmentRawRequest.getcorrespondenceattachmentsbyrawrequestid(rawrequestid)
        _correspondenceemails = FOIApplicantCorrespondenceEmailRawRequest.getapplicantcorrespondenceemails(rawrequestid)
        if ministryrequestid != 'None':
            _correspondencelogs.extend(FOIApplicantCorrespondence.getapplicantcorrespondences(ministryrequestid))
            _correspondenceattachments.extend(FOIApplicantCorrespondenceAttachment.getcorrespondenceattachmentsbyministryid(ministryrequestid))
            _correspondenceemails.extend(FOIApplicantCorrespondenceEmail.getapplicantcorrespondenceemails(ministryrequestid))
        correspondencelogs =[]
        for _correpondencelog in _correspondencelogs:
                attachments = []
                for _attachment in self.__getattachmentsbyid(_correspondenceattachments, _correpondencelog['applicantcorrespondenceid'], _correpondencelog['version']):
                    attachment = {
                        "applicantcorrespondenceattachmentid" : _attachment['applicantcorrespondenceattachmentid'],
                        "documenturipath" : _attachment['attachmentdocumenturipath'],
                        "filename" : _attachment['attachmentfilename'],
                    }
                    attachments.append(attachment)
                correpondencelog = self.__createcorrespondencelog(_correpondencelog, attachments)
                #Email block - Begin
                correpondencelog['emails'] = self.__getcorrespondenceemailbyid(_correspondenceemails,  _correpondencelog['applicantcorrespondenceid'], _correpondencelog['version'])
                #Email block - End
                correspondencelogs.append(correpondencelog)
        # Since we're merging raw and ministry requests, resort by date
        correspondencelogs.sort(key=lambda x: datetime.strptime(x['date'], '%Y %b %d | %I:%M %p'), reverse=True)
        return correspondencelogs
    
    def __getattachmentsbyid(self, attachments, correspondenceid, correspondenceversion):
        return [x for x in attachments if x['applicantcorrespondenceid'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]

    def __getcorrespondenceemailbyid(self, emails, correspondenceid, correspondenceversion):
        return [x['correspondence_to'] for x in emails if x['applicantcorrespondence_id'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]
    
    def saveapplicantcorrespondencelog(self, requestid, ministryrequestid, data, userid, isdraft=False):
        applicantcorrespondence = FOIApplicantCorrespondence()
        if "correspondenceid" in data and data['correspondenceid'] is not None:
            correspondence = FOIApplicantCorrespondence.getapplicantcorrespondencebyid(data['correspondenceid'])
            applicantcorrespondence.applicantcorrespondenceid = data['correspondenceid']
            applicantcorrespondence.version = correspondence['version']+1
        else:
            applicantcorrespondence.version=1
        applicantcorrespondence.templateid =  data['templateid'] if 'templateid' in data else None
        applicantcorrespondence.isresponse = False if 'templateid' in data else True
        applicantcorrespondence.foiministryrequest_id = ministryrequestid
        applicantcorrespondence.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        applicantcorrespondence.isdraft = isdraft
        if userid == 'system':
            applicantcorrespondence.sentcorrespondencemessage = data['correspondencemessagejson']
            applicantcorrespondence.sentby = 'System Generated Email'
            applicantcorrespondence.sent_at = datetime.now()
        else:
            applicantcorrespondence.correspondencemessagejson = data['correspondencemessagejson'] if 'correspondencemessagejson' in data else None
            applicantcorrespondence.createdby = userid  
            if 'emails' in data and len(data["emails"]) > 0:
                applicantcorrespondence.sent_at = datetime.now()
                applicantcorrespondence.sentby = userid
        emails = data['emails'] if 'emails' in data else None   
        applicantcorrespondence.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()

        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondence,data['attachments'], emails)        

    def saveapplicantcorrespondencelogforrawrequest(self, requestid, data, userid, isdraft=False):
        applicantcorrespondence = FOIApplicantCorrespondenceRawRequest()
        if "correspondenceid" in data and data['correspondenceid'] is not None:
            correspondence = FOIApplicantCorrespondenceRawRequest.getapplicantcorrespondencebyid(data['correspondenceid'])
            applicantcorrespondence.applicantcorrespondenceid = data['correspondenceid']
            applicantcorrespondence.version = correspondence['version']+1
        else:
            applicantcorrespondence.version=1
        applicantcorrespondence.foirawrequest_id = requestid
        applicantcorrespondence.foirawrequestversion_id =FOIRawRequest.getversionforrequest(requestid=requestid)

        applicantcorrespondence.templateid =  data['templateid'] if 'templateid' in data else None
        applicantcorrespondence.isresponse = False if 'templateid' in data else True
        applicantcorrespondence.isdraft = isdraft
        if userid == 'system':
            applicantcorrespondence.sentcorrespondencemessage = data['correspondencemessagejson']
            applicantcorrespondence.sentby = 'System Generated Email'
            applicantcorrespondence.sent_at = datetime.now()
        else:
            #try commenting out the line below when sending ministry request - see if it still causes error
            applicantcorrespondence.correspondencemessagejson = data['correspondencemessagejson'] if 'correspondencemessagejson' in data else None
            applicantcorrespondence.createdby = userid  
            if 'emails' in data and len(data["emails"]) > 0:
                applicantcorrespondence.sent_at = datetime.now()
                applicantcorrespondence.sentby = userid
        emails = data['emails'] if 'emails' in data else None   
        applicantcorrespondence.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
        return FOIApplicantCorrespondenceRawRequest.saveapplicantcorrespondence(applicantcorrespondence,data['attachments'], emails)
    
    def editapplicantcorrespondencelogforministry(self, ministryrequestid, data, userid):
        correspondence = FOIApplicantCorrespondence.getapplicantcorrespondencebyid(data['correspondenceid'])
        updt_correspondence = FOIApplicantCorrespondence()
        updt_correspondence.__dict__.update(correspondence)
        updt_correspondence.version = correspondence['version']+1
        updt_correspondence.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        updt_correspondence.created_at = datetime.now()
        updt_correspondence.createdby = userid
        if 'emails' in data and len(data["emails"]) > 0:
            updt_correspondence.sent_at = datetime.now()
            updt_correspondence.sentby = userid
        if 'responsedate' in data and data['responsedate'] is not None:
            updt_correspondence.response_at = data['responsedate'] + ' ' + datetime.now().time().strftime("%H:%M:%S")
        if 'isdraft' in data and data['isdraft'] is not None:
            updt_correspondence.isdraft = data['isdraft']
        if 'correspondencemessagejson' in data and data['correspondencemessagejson'] is not None:
            updt_correspondence.correspondencemessagejson = data['correspondencemessagejson']
        response = FOIApplicantCorrespondence.saveapplicantcorrespondence(updt_correspondence, None, None)
        if response.success == True:
            attachresponse = self.__updateattachmentversionministry(data, userid)
            return response
        return response
    
    def editapplicantcorrespondencelogforrawrequest(self, rawrequestid, data, userid):
        correspondence = FOIApplicantCorrespondenceRawRequest.getapplicantcorrespondencebyid(data['correspondenceid'])
        updt_correspondence = FOIApplicantCorrespondenceRawRequest()
        updt_correspondence.__dict__.update(correspondence)
        updt_correspondence.version = correspondence['version']+1
        updt_correspondence.foirawrequestversion_id =FOIRawRequest.getversionforrequest(requestid=rawrequestid)
        updt_correspondence.created_at = datetime.now()
        updt_correspondence.createdby = userid
        # This is for sent correspondences
        if 'emails' in data and len(data["emails"]) > 0:
            updt_correspondence.sent_at = datetime.now()
            updt_correspondence.sentby = userid
        if 'responsedate' in data and data['responsedate'] is not None:
            updt_correspondence.response_at = data['responsedate'] + ' ' + datetime.now().time().strftime("%H:%M:%S")
        if 'isdraft' in data and data['isdraft'] is not None:
            updt_correspondence.isdraft = data['isdraft']
        if 'correspondencemessagejson' in data and data['correspondencemessagejson'] is not None:
            updt_correspondence.correspondencemessagejson = data['correspondencemessagejson']
        response = FOIApplicantCorrespondenceRawRequest.saveapplicantcorrespondence(updt_correspondence, None, None)
        if response.success == True:
            attachresponse = self.__updateattachmentversionrawrequest(data, userid)
            return response
        return response

    def deleteapplicantcorrespondencelogministry(self, ministryrequestid, correpondenceid, userid):
        return FOIApplicantCorrespondence.deleteapplicantcorrespondence(ministryrequestid,correpondenceid,userid)        
    
    def deleteapplicantcorrespondencelograwrequest(self, rawrequestid, correpondenceid, userid):
        return FOIApplicantCorrespondenceRawRequest.deleteapplicantcorrespondence(rawrequestid, correpondenceid,userid)

    def saveapplicantcorrespondenceresponselog(self, ministryrequestid, data, userid):
        result = self.saveapplicantcorrespondencelog(None, ministryrequestid, data, userid)
        if result.success == True:
            correspondenceresponse = FOIApplicantCorrespondenceResponse()
            correspondenceresponse.applicantcorrespondence_id = result.identifier
            correspondenceresponse.applicantcorrespondenceversion_id = 1
            correspondenceresponse.created_at = datetime.now()
            correspondenceresponse.createdby = userid
            correspondenceresponse.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
            correspondenceresponse.version=1
            return FOIApplicantCorrespondenceResponse.saveapplicantcorrespondenceresponse(correspondenceresponse)
    
    def updateapplicantcorrespondencelog(self, correspondenceid, content):
        return FOIApplicantCorrespondence.updatesentcorrespondence(correspondenceid, content)
    
    def getapplicantcorrespondencelogbyid(self, applicantcorrespondenceid):
        applicantcorrespondence =  FOIApplicantCorrespondence.getapplicantcorrespondencebyid(applicantcorrespondenceid)
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(applicantcorrespondence["correspondencemessagejson"])
        emailhtml_decoded_string = html.unescape(self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml'))
        return emailhtml_decoded_string if _isjson else _correspondencemessagejson

    def getlatestapplicantcorrespondence(self, ministryid):
        return FOIApplicantCorrespondence().getlatestapplicantcorrespondence(ministryid)
    
    def __updateattachmentversionministry(self, data, userid):
        # Check for attachments
        attachment = FOIApplicantCorrespondenceAttachment.getcorrespondenceattachmentbyapplicantcorrespondenceid(data['correspondenceid'])
        if len(attachment) > 0:
            updated_attachment = FOIApplicantCorrespondenceAttachment()
            updated_attachment.__dict__.update(attachment)
            if 'filename' in data and data['filename'] is not None:
                updated_attachment.attachmentfilename = data['filename']
            updated_attachment.created_at = datetime.now()
            updated_attachment.createdby = userid
            updated_attachment.version=attachment["version"]+1
            updated_attachment.applicantcorrespondence_version = attachment["applicantcorrespondence_version"] + 1
            response = FOIApplicantCorrespondenceAttachment.saveapplicantcorrespondenceattachment(updated_attachment)
            return response

    def __updateattachmentversionrawrequest(self, data, userid):
        # Check for attachments
        attachment = FOIApplicantCorrespondenceAttachmentRawRequest.getcorrespondenceattachmentbyapplicantcorrespondenceid(data['correspondenceid'])
        if len(attachment) > 0:
            updated_attachment = FOIApplicantCorrespondenceAttachmentRawRequest()
            updated_attachment.__dict__.update(attachment)
            if 'filename' in data and data['filename'] is not None:
                updated_attachment.attachmentfilename = data['filename']
            updated_attachment.created_at = datetime.now()
            updated_attachment.createdby = userid
            updated_attachment.version=attachment["version"]+1
            updated_attachment.applicantcorrespondence_version = attachment["applicantcorrespondence_version"] + 1
            response = FOIApplicantCorrespondenceAttachmentRawRequest.saveapplicantcorrespondenceattachment(updated_attachment)
            return response

    def __createcorrespondencelog(self, _correpondencelog, attachments):
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(_correpondencelog['correspondencemessagejson']) if _correpondencelog['correspondencemessagejson'] is not None else (None, None)
        _sentcorrespondencemessagejson = json.loads(_correpondencelog["sentcorrespondencemessage"]) if _correpondencelog['sentcorrespondencemessage'] not in [None,''] else None
        issentmessage = _sentcorrespondencemessagejson is not None and 'sent_at' in _correpondencelog and _correpondencelog['sent_at'] is not None
        _date = self.__pstformat(_correpondencelog['sent_at']) if issentmessage else self.__pstformat(_correpondencelog['created_at'])
        if "response_at" in _correpondencelog and _correpondencelog["response_at"] is not None:
            _date = self.__pstformat(_correpondencelog["response_at"])
        correpondencelog ={
            "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
            "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
            "templateid":_correpondencelog['templateid'],
            "text": self.__getvaluefromschema(_sentcorrespondencemessagejson, 'message') if _sentcorrespondencemessagejson is not None else self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml') if _isjson else None,
            "id": self.__getvaluefromjson(_correspondencemessagejson, 'id') if _isjson else None,
            "type": self.__getvaluefromjson(_correspondencemessagejson, 'type') if _isjson else None,
            "created_at":self.__pstformat(_correpondencelog['created_at']),
            "createdby":_correpondencelog['createdby'] if  _correpondencelog['createdby'] is not None else _correpondencelog['sentby'],
            "date": _date,
            "sentby": _correpondencelog["sentby"],
            "userId": _correpondencelog['createdby'] if  _correpondencelog['createdby'] is not None else _correpondencelog['sentby'],
            "attachments" : attachments,
            "category" : self.__getcorrespondencecategory(_correpondencelog),
            "israwrequest": _correpondencelog.get('israwrequest', False) is True,
        }        
        return correpondencelog
    
    def __getcorrespondencecategory(self, _correpondencelog):
        if _correpondencelog['isdraft']== True:
            return "draft"
        if _correpondencelog["isresponse"] == True:
            return "response"
        return "correspondence"

    def __getjsonobject(self, correspondencemessagejson):
        try:
            data = json.loads(correspondencemessagejson)
        except ValueError:
            return correspondencemessagejson, False
        return data, True

    def __getvaluefromjson(self, jsonobject, property):
        return jsonobject[property] if jsonobject is not None and property in jsonobject else None

    def __pstformat(self, _date):
        return maya.parse(_date).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p')
    
    def __getvaluefromschema(self, schema, property):
        return schema.get(property) if property in schema  else None