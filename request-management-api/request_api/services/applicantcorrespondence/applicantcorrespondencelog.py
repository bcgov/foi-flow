from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
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
        correspondencelogs =[]
        for _correpondencelog in _correspondencelogs:
                attachments = []
                for _attachment in _correpondencelog['attachments']:
                    attachment = {
                        "applicantcorrespondenceattachmentid" : _attachment.applicantcorrespondenceattachmentid,
                        "documenturipath" : _attachment.attachmentdocumenturipath,
                        "filename" : _attachment.attachmentfilename,
                    }
                    attachments.append(attachment)
                correpondencelog = self.__createcorrespondencelog(_correpondencelog, attachments)
                correspondencelogs.append(correpondencelog)
        return correspondencelogs

    def saveapplicantcorrespondencelog(self, requestid, ministryrequestid, data, userid):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.templateid = data['templateid']
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        if userid == 'system':
            applicantcorrespondencelog.sentcorrespondencemessage = data['correspondencemessagejson']
            applicantcorrespondencelog.sentby = 'System Generated Email'
            applicantcorrespondencelog.sent_at = datetime.now()
        else:
            applicantcorrespondencelog.correspondencemessagejson = data['correspondencemessagejson']
            applicantcorrespondencelog.createdby = userid       
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog,data['attachments'])        
       

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
            "created_at":_correpondencelog['sent_at'] if _sentcorrespondencemessagejson is not None else _correpondencelog['created_at'],
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