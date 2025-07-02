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

from sqlalchemy.sql.expression import null
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
        print('**_correspondencelogs: ', _correspondencelogs)
        _correspondenceattachments = FOIApplicantCorrespondenceAttachmentRawRequest.getcorrespondenceattachmentsbyrawrequestid(rawrequestid)
        print('**_correspondenceattachments: ', _correspondenceattachments)
        _correspondenceemails = FOIApplicantCorrespondenceEmailRawRequest.getapplicantcorrespondenceemails(rawrequestid)
        print('**_correspondenceemails: ', _correspondenceemails)
        if ministryrequestid != 'None':
            print('getting FOIApplicantCorrespondence')
            _correspondencelogs.extend(FOIApplicantCorrespondence.getapplicantcorrespondences(ministryrequestid))
            print('getting FOIApplicantCorrespondenceAttachment')
            _correspondenceattachments.extend(FOIApplicantCorrespondenceAttachment.getcorrespondenceattachmentsbyministryid(ministryrequestid))
            print('getting FOIApplicantCorrespondenceEmail')
            _correspondenceemails.extend(FOIApplicantCorrespondenceEmail.getapplicantcorrespondenceemails(ministryrequestid))
        print('****Final:')
        print('_correspondencelogs: ', _correspondencelogs)
        print('_correspondenceattachments: ', _correspondenceattachments)
        print('_correspondenceemails: ', _correspondenceemails)
        correspondencelogs =[]
        for _correpondencelog in _correspondencelogs:
                attachments = []
                print('getting attachments')
                for _attachment in self.__getattachmentsbyid(_correspondenceattachments, _correpondencelog['applicantcorrespondenceid'], _correpondencelog['version']):
                    print('formatting attachments')
                    attachment = {
                        "applicantcorrespondenceattachmentid" : _attachment['applicantcorrespondenceattachmentid'],
                        "documenturipath" : _attachment['attachmentdocumenturipath'],
                        "filename" : _attachment['attachmentfilename'],
                    }
                    print('appending attachments')
                    attachments.append(attachment)
                print('attachment appended')
                print('creating correspondence log')
                correpondencelog = self.__createcorrespondencelog(_correpondencelog, attachments)
                #Email block - Begin
                print('getting emails')
                correpondencelog['emails'] = self.__getcorrespondenceemailbyid(_correspondenceemails,  _correpondencelog['applicantcorrespondenceid'], _correpondencelog['version'])
                print('getting ccemails')
                correpondencelog['ccemails'] = self.__getcorrespondenceCCemailbyid(_correspondenceemails,  _correpondencelog['applicantcorrespondenceid'], _correpondencelog['version'])
                #Email block - End
                print('appending logs')
                correspondencelogs.append(correpondencelog)
        # Since we're merging raw and ministry requests, resort by date
        print('sorting logs')
        correspondencelogs.sort(key=lambda x: datetime.strptime(x['date'], '%Y %b %d | %I:%M %p'), reverse=True)
        print('returning logs')
        return correspondencelogs
    
    def __getattachmentsbyid(self, attachments, correspondenceid, correspondenceversion):
        return [x for x in attachments if x['applicantcorrespondenceid'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]

    def __getcorrespondenceemailbyid(self, emails, correspondenceid, correspondenceversion):
        return [x['correspondence_to'] for x in emails if x['applicantcorrespondence_id'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion and x['iscarboncopy'] is not True]

    def __getcorrespondenceCCemailbyid(self, emails, correspondenceid, correspondenceversion):
        return [x['correspondence_to'] for x in emails if x['applicantcorrespondence_id'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion and x['iscarboncopy'] is True]
    
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
        ccemails = data['ccemails'] if 'ccemails' in data else None
        applicantcorrespondence.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
        applicantcorrespondence.templatename = data['templatename'] if 'templatename' in data and data['templatename'] is not None else None
        applicantcorrespondence.templatetype = data['templatetype'] if 'templatetype' in data and data['templatetype'] is not None else None
        applicantcorrespondence.emailsubject = data['emailsubject'] if 'emailsubject' in data else ''
        if 'correspondencesubject' in data: applicantcorrespondence.correspondencesubject = data['correspondencesubject']
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondence,data['attachments'], emails, ccemails)

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
            applicantcorrespondence.sentby = userid
            applicantcorrespondence.sent_at = datetime.now()
        else:
            #try commenting out the line below when sending ministry request - see if it still causes error
            applicantcorrespondence.correspondencemessagejson = data['correspondencemessagejson'] if 'correspondencemessagejson' in data else None
            applicantcorrespondence.createdby = userid  
            if 'emails' in data and len(data["emails"]) > 0:
                applicantcorrespondence.sent_at = datetime.now()
                applicantcorrespondence.sentby = userid
        emails = data['emails'] if 'emails' in data else None   
        ccemails = data['ccemails'] if 'ccemails' in data else None
        applicantcorrespondence.response_at = data['responsedate'] if 'responsedate' in data and data['responsedate'] is not None else datetime.now()
        applicantcorrespondence.templatename = data['templatename'] if 'templatename' in data and data['templatename'] is not None else None
        applicantcorrespondence.templatetype = data['templatetype'] if 'templatetype' in data and data['templatetype'] is not None else None
        applicantcorrespondence.emailsubject = data['emailsubject'] if 'emailsubject' in data else ''
        if 'correspondencesubject' in data: applicantcorrespondence.correspondencesubject = data['correspondencesubject']
        return FOIApplicantCorrespondenceRawRequest.saveapplicantcorrespondence(applicantcorrespondence,data['attachments'], emails, ccemails)
    
    def editapplicantcorrespondencelogforministry(self, ministryrequestid, data, userid):
        correspondence = FOIApplicantCorrespondence.getapplicantcorrespondencebyid(data['correspondenceid'])
        oldcorrespondenceid = correspondence['applicantcorrespondenceid']
        oldcorrespondenceversion = correspondence['version']
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
            updt_correspondence.response_at = data['responsedate']
        if 'isdraft' in data and data['isdraft'] is not None:
            updt_correspondence.isdraft = data['isdraft']
        if 'correspondencemessagejson' in data and data['correspondencemessagejson'] is not None:
            updt_correspondence.correspondencemessagejson = data['correspondencemessagejson']
        if 'subject' in data:
            if 'correspondencemessagejson' in correspondence and correspondence['correspondencemessagejson'] is not None:
                correspondencemessagejson = json.loads(correspondence['correspondencemessagejson'])
            else:
                correspondencemessagejson = {}
            correspondencemessagejson['subject'] = data['subject']
            updt_correspondence.correspondencemessagejson = json.dumps(correspondencemessagejson)
        if updt_correspondence.sentcorrespondencemessage is None: updt_correspondence.sentcorrespondencemessage = null()
        response = FOIApplicantCorrespondence.saveapplicantcorrespondence(updt_correspondence, None, None)
        if response.success == True:
            attachresponse = self.__updateattachmentsversionministryrequest(ministryrequestid, data, oldcorrespondenceid, oldcorrespondenceversion, userid)
            emailsresponse = self.__updateemailsversionministryrequest(ministryrequestid, oldcorrespondenceid, oldcorrespondenceversion, userid)
            return response
        return response
    
    def editapplicantcorrespondencelogforrawrequest(self, rawrequestid, data, userid):
        correspondence = FOIApplicantCorrespondenceRawRequest.getapplicantcorrespondencebyid(data['correspondenceid'])
        oldcorrespondenceid = correspondence['applicantcorrespondenceid']
        oldcorrespondenceversion = correspondence['version']
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
            updt_correspondence.response_at = data['responsedate']
        if 'isdraft' in data and data['isdraft'] is not None:
            updt_correspondence.isdraft = data['isdraft']
        if 'correspondencemessagejson' in data and data['correspondencemessagejson'] is not None:
            updt_correspondence.correspondencemessagejson = data['correspondencemessagejson']
        if 'subject' in data:
            if 'correspondencemessagejson' in correspondence and correspondence['correspondencemessagejson'] is not None:
                correspondencemessagejson = json.loads(correspondence['correspondencemessagejson'])
            else:
                correspondencemessagejson = {}
            correspondencemessagejson['subject'] = data['subject']
            updt_correspondence.correspondencemessagejson = json.dumps(correspondencemessagejson)
        if updt_correspondence.sentcorrespondencemessage is None: updt_correspondence.sentcorrespondencemessage = null()
        response = FOIApplicantCorrespondenceRawRequest.saveapplicantcorrespondence(updt_correspondence, None, None)
        if response.success == True:
            attachresponse = self.__updateattachmentsversionrawrequest(rawrequestid, data, oldcorrespondenceid, oldcorrespondenceversion, userid)
            emailsresponse = self.__updateemailsversionrawrequest(rawrequestid, oldcorrespondenceid, oldcorrespondenceversion, userid)
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
    
    def __updateattachmentsversionministryrequest(self, ministryrequestid, data, oldcorrespondenceid, oldcorrespondenceversion, userid):
        # Check for attachments
        attachments = FOIApplicantCorrespondenceAttachment.getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(oldcorrespondenceid)
        updated_attachments = []
        if (attachments is not None and len(attachments) > 0):
            for _attachment in attachments:
                updated_attachment = FOIApplicantCorrespondenceAttachment()
                updated_attachment.__dict__.update(_attachment)
                if 'filename' in data and data['filename'] is not None and _attachment['applicantcorrespondenceattachmentid'] == data['correspondenceattachmentid']:
                    updated_attachment.attachmentfilename = data['filename']
                updated_attachment.created_at = _attachment['created_at']
                updated_attachment.updated_at = datetime.now()
                updated_attachment.createdby = _attachment['createdby']
                updated_attachment.updatedby = userid
                updated_attachment.version=_attachment["version"]+1
                updated_attachment.applicantcorrespondenceid = oldcorrespondenceid
                updated_attachment.applicantcorrespondence_version = oldcorrespondenceversion + 1
                updated_attachments.append(updated_attachment)
            response = FOIApplicantCorrespondenceAttachment.saveapplicantcorrespondenceattachments(ministryrequestid, updated_attachments)
            return response

    def __updateattachmentsversionrawrequest(self, rawrequestid, data, oldcorrespondenceid, oldcorrespondenceversion, userid):
        # Check for attachments
        attachments = FOIApplicantCorrespondenceAttachmentRawRequest.getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(oldcorrespondenceid)
        updated_attachments = []
        if (attachments is not None and len(attachments) > 0):
            for _attachment in attachments:
                updated_attachment = FOIApplicantCorrespondenceAttachmentRawRequest()
                updated_attachment.__dict__.update(_attachment)
                if 'filename' in data and data['filename'] is not None and _attachment['applicantcorrespondenceattachmentid'] == data['correspondenceattachmentid']:
                    updated_attachment.attachmentfilename = data['filename']
                updated_attachment.created_at = _attachment['created_at']
                updated_attachment.updated_at = datetime.now()
                updated_attachment.createdby = _attachment['createdby']
                updated_attachment.updatedby = userid
                updated_attachment.version=_attachment["version"]+1
                updated_attachment.applicantcorrespondenceid = oldcorrespondenceid
                updated_attachment.applicantcorrespondence_version = oldcorrespondenceversion + 1
                updated_attachments.append(updated_attachment)
            response = FOIApplicantCorrespondenceAttachmentRawRequest.saveapplicantcorrespondenceattachments(rawrequestid, updated_attachments)
            return response

    def __updateemailsversionrawrequest(self, rawrequestid, oldcorrespondencelogid, oldcorrespondenceversion, userid):
        emails = FOIApplicantCorrespondenceEmailRawRequest().getapplicantcorrespondenceemails(rawrequestid)
        emailsbycorrespondence = self.__getemailsincorrespondence(emails, oldcorrespondencelogid, oldcorrespondenceversion)
        correspondenceemails = []
        if(emailsbycorrespondence is not None and len(emailsbycorrespondence) > 0):
            for _email in emailsbycorrespondence:
                email = FOIApplicantCorrespondenceEmailRawRequest()
                email.__dict__.update(_email)
                email.applicantcorrespondence_id = oldcorrespondencelogid
                email.applicantcorrespondence_version = oldcorrespondenceversion + 1
                email.updatedby = userid
                correspondenceemails.append(email)
            FOIApplicantCorrespondenceEmailRawRequest().saveapplicantcorrespondenceemail(oldcorrespondencelogid, correspondenceemails)

    def __updateemailsversionministryrequest(self, ministryrequestid, oldcorrespondencelogid, oldcorrespondenceversion, userid):
        emails = FOIApplicantCorrespondenceEmail().getapplicantcorrespondenceemails(ministryrequestid)
        emailsbycorrespondence = self.__getemailsincorrespondence(emails, oldcorrespondencelogid, oldcorrespondenceversion)
        correspondenceemails = []
        if(emailsbycorrespondence is not None and len(emailsbycorrespondence) > 0):
            for _email in emailsbycorrespondence:
                email = FOIApplicantCorrespondenceEmail()
                email.__dict__.update(_email)
                email.applicantcorrespondence_id = oldcorrespondencelogid
                email.applicantcorrespondence_version = oldcorrespondenceversion + 1
                email.updatedby = userid
                correspondenceemails.append(email)
            FOIApplicantCorrespondenceEmail().saveapplicantcorrespondenceemail(oldcorrespondencelogid, correspondenceemails)

    def __getemailsincorrespondence(self, emails, correspondenceid, correspondenceversion):
        return [x for x in emails if x['applicantcorrespondence_id'] == correspondenceid and x['applicantcorrespondence_version'] == correspondenceversion]

    def __createcorrespondencelog(self, _correpondencelog, attachments):
        print('getting jsonobject')
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(_correpondencelog['correspondencemessagejson']) if _correpondencelog['correspondencemessagejson'] is not None else (None, None)
        print('loading _sentcorrespondencemessagejson')
        _sentcorrespondencemessagejson = json.loads(_correpondencelog["sentcorrespondencemessage"]) if _correpondencelog['sentcorrespondencemessage'] not in [None,''] else None
        print('getting issentmessgae')
        issentmessage = _sentcorrespondencemessagejson is not None and 'sent_at' in _correpondencelog and _correpondencelog['sent_at'] is not None
        print('getting _date')
        _date = self.__pstformat(_correpondencelog['sent_at']) if issentmessage else self.__pstformat(_correpondencelog['created_at'])
        if "response_at" in _correpondencelog and _correpondencelog["response_at"] is not None:
            print('overwriting _date from response_at')
            _date = self.__pstformat(_correpondencelog["response_at"])
        print('formatting correpondencelog')
        correpondencelog ={
            "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
            "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
            "templateid":_correpondencelog['templateid'],
            "text": self.__getvaluefromschema(_sentcorrespondencemessagejson, 'message') if _sentcorrespondencemessagejson is not None else self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml') if _isjson else None,
            "subject": self.__getvaluefromjson(_correspondencemessagejson, 'subject') if _isjson else None,
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
            "draft": self.__getvaluefromjson(_correspondencemessagejson, 'emaildraft') if _isjson else None,
            "templatename": _correpondencelog['templatename'],
            "templatetype": _correpondencelog['templatetype'],
            "emailsubject": _correpondencelog['emailsubject'],
            "correspondencesubject": _correpondencelog['correspondencesubject'],
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