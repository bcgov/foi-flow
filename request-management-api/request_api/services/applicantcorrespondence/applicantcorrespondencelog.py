from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
from request_api.models.FOIApplicantCorrespondenceAttachments import FOIApplicantCorrespondenceAttachment
from request_api.models.FOIApplicantCorrespondenceResponses import FOIApplicantCorrespondenceResponse
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

import maya
import json
import html
from datetime import datetime
class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()
    
    def gettemplatebyid(self, templateid):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.get_template_by_id(templateid)

    def getapplicantcorrespondencelogs(self,ministryrequestid):
        """ Returns the active applicant correspondence logs
        """
        _correspondencelogs = FOIApplicantCorrespondence.getapplicantcorrespondences(ministryrequestid)
        _correspondenceattachments = FOIApplicantCorrespondenceAttachment.getcorrespondenceattachmentsbyministryid(ministryrequestid)
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
                correspondencelogs.append(correpondencelog)
        return correspondencelogs
    
    def __getattachmentsbyid(self, attachments, correspondenceid, correspondenceversion):
        return [x for x in attachments if x['applicantcorrespondenceid'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]

    def saveapplicantcorrespondencelog(self, requestid, ministryrequestid, data, userid, isdraft=False):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.version = 1
        applicantcorrespondencelog.templateid = data['templateid']
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        applicantcorrespondencelog.isdraft = isdraft
        if userid == 'system':
            applicantcorrespondencelog.sentcorrespondencemessage = data['correspondencemessagejson']
            applicantcorrespondencelog.sentby = 'System Generated Email'
            applicantcorrespondencelog.sent_at = datetime.now()
        else:
            applicantcorrespondencelog.correspondencemessagejson = data['correspondencemessagejson']
            applicantcorrespondencelog.createdby = userid       
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog,data['attachments'], data['emails'])        
    
    def saveapplicantcorrespondenceresponselog(self, ministryrequestid, data, userid):
        attachments = []
        applicantcorrespondenceid = data['applicantcorrespondenceid'] if 'applicantcorrespondenceid' in data and data['applicantcorrespondenceid'] is not None else None
        correspondenceresponse = FOIApplicantCorrespondenceResponse()
        correspondenceresponse.applicantcorrespondenceid = applicantcorrespondenceid
        correspondenceresponse.foiministryrequest_id = ministryrequestid
        correspondenceresponse.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        correspondenceresponse.created_at = datetime.now()
        correspondenceresponse.createdby = userid
        correspondenceresponse.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
        correspondenceresponse.version=1
        response = FOIApplicantCorrespondenceResponse.saveapplicantcorrespondenceresponse(correspondenceresponse)
        if response.success == True:
            for attachment in data['attachments']:
                correspondenceattachment = FOIApplicantCorrespondenceAttachment()
                correspondenceattachment.applicantcorrespondenceid = applicantcorrespondenceid
                correspondenceattachment.attachmentdocumenturipath = attachment['url']
                correspondenceattachment.attachmentfilename = attachment['filename']
                correspondenceattachment.created_at = datetime.now()
                correspondenceattachment.createdby = userid
                correspondenceattachment.version=1
                correspondenceattachment.isresponse = True
                correspondenceattachment.applicantcorrespondenceresponseid = response.identifier
                attachments.append(correspondenceattachment)
            return FOIApplicantCorrespondenceAttachment.saveapplicantcorrespondenceattachments(ministryrequestid, attachments)

    def editapplicantcorrespondenceresponselog(self, ministryrequestid, data, userid):
        correspondence_response = FOIApplicantCorrespondenceResponse.getapplicantcorrespondenceresponse(data['correspondenceresponseid'])
        updt_correspondence_response = FOIApplicantCorrespondenceResponse()
        updt_correspondence_response.__dict__.update(correspondence_response)
        updt_correspondence_response.version = correspondence_response['version']+1
        updt_correspondence_response.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        updt_correspondence_response.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
        updt_correspondence_response.created_at = datetime.now()
        updt_correspondence_response.createdby = userid
        response = FOIApplicantCorrespondenceResponse.saveapplicantcorrespondenceresponse(updt_correspondence_response)
        if 'correspondenceattachmentid' in data and data['filename'] is not None:
            attachment = FOIApplicantCorrespondenceAttachment.getapplicantcorrespondenceattachmentbyid(data['correspondenceattachmentid'])
            updt_attachment = FOIApplicantCorrespondenceAttachment()
            updt_attachment.__dict__.update(attachment)
            updt_attachment.attachmentfilename = data['filename']
            updt_attachment.created_at = datetime.now()
            updt_attachment.createdby = userid
            updt_attachment.version=attachment['version']+1
            FOIApplicantCorrespondenceAttachment.saveapplicantcorrespondenceattachment(updt_attachment)
        return response
    
    def updateapplicantcorrespondencelog(self, correspondenceid, content):
        return FOIApplicantCorrespondence.updatesentcorrespondence(correspondenceid, content)
    
    def getapplicantcorrespondencelogbyid(self, applicantcorrespondenceid):
        applicantcorrespondence =  FOIApplicantCorrespondence.getapplicantcorrespondencebyid(applicantcorrespondenceid)
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(applicantcorrespondence["correspondencemessagejson"])
        emailhtml_decoded_string = html.unescape(self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml'))
        return emailhtml_decoded_string if _isjson else _correspondencemessagejson

    def getlatestapplicantcorrespondence(self, ministryid):
        return FOIApplicantCorrespondence().getlatestapplicantcorrespondence(ministryid)
    
    def __createcorrespondencelog(self, _correpondencelog, attachments):
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(_correpondencelog['correspondencemessagejson']) if _correpondencelog['correspondencemessagejson'] is not None else (None, None)
        _sentcorrespondencemessagejson = json.loads(_correpondencelog["sentcorrespondencemessage"]) if _correpondencelog['sentcorrespondencemessage'] not in [None,''] else None
        correpondencelog ={
            "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
            "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
            "templateid":_correpondencelog['templateid'],
            "text": self.__getvaluefromschema(_sentcorrespondencemessagejson, 'message') if _sentcorrespondencemessagejson is not None else self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml') if _isjson else None,
            "id": self.__getvaluefromjson(_correspondencemessagejson, 'id') if _isjson else None,
            "type": self.__getvaluefromjson(_correspondencemessagejson, 'type') if _isjson else None,
            "created_at":self.__pstformat(_correpondencelog['sent_at']) if _sentcorrespondencemessagejson is not None else self.__pstformat(_correpondencelog['created_at']),
            "createdby":_correpondencelog['createdby'] if  _correpondencelog['createdby'] is not None else _correpondencelog['sentby'],
            "date": self.__pstformat(_correpondencelog['sent_at']) if _sentcorrespondencemessagejson is not None else self.__pstformat(_correpondencelog['created_at']),
            "userId": _correpondencelog['createdby'] if  _correpondencelog['createdby'] is not None else _correpondencelog['sentby'],
            "attachments" : attachments
        }        
        return correpondencelog

    def __getjsonobject(self, correspondencemessagejson):
        try:
            data = json.loads(correspondencemessagejson)
        except ValueError:
            return correspondencemessagejson, False
        return data, True

    def __getvaluefromjson(self, jsonobject, property):
        return jsonobject[property] if jsonobject is not None else None

    def __pstformat(self, _date):
        return maya.parse(_date).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p')
    
    def __getvaluefromschema(self, schema, property):
        return schema.get(property) if property in schema  else None