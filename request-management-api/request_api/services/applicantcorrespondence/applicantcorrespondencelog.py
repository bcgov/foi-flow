from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import maya
import json
class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()
    
    def gettemplatebyid(self, templateid):
        """ Returns the active applicant correspondence templates
        """
        print("templateid in gettemplatebyid = ", templateid)
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
                (_correspondencemessagejson, _isjson) = self.__getjsonobject(_correpondencelog['correspondencemessagejson'])
                correpondencelog ={
                    "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
                    "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
                    "templateid":_correpondencelog['templateid'],
                    "text":self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml') if _isjson else _correspondencemessagejson,
                    "id": self.__getvaluefromjson(_correspondencemessagejson, 'id') if _isjson else None,
                    "type": self.__getvaluefromjson(_correspondencemessagejson, 'type') if _isjson else None,
                    "created_at":_correpondencelog['created_at'],
                    "createdby":_correpondencelog['createdby'],
                    "date": maya.parse(_correpondencelog["created_at"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p'),
                    "userId":_correpondencelog['createdby'],
                    "attachments" : attachments
                }
                correspondencelogs.append(correpondencelog)
        return correspondencelogs

    def saveapplicantcorrespondencelog(self,templateid,ministryrequestid,createdby,messagehtml,attachments):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.templateid = templateid
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.correspondencemessagejson = messagehtml
        applicantcorrespondencelog.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        applicantcorrespondencelog.createdby = createdby
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog,attachments)
    
    def getapplicantcorrespondencelogbyid(self, applicantcorrespondenceid):
        return FOIApplicantCorrespondence.getapplicantcorrespondencebyid(applicantcorrespondenceid)



    def __getjsonobject(self, correspondencemessagejson):
        try:
            data = json.loads(correspondencemessagejson)
        except ValueError:
            return correspondencemessagejson, False
        return data, True

    def __getvaluefromjson(self, jsonobject, property):
        return jsonobject[property] if property in jsonobject else ""
