from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import maya
import json
from html.parser import HTMLParser
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
                _sentcorrespondencemessagejson = json.loads(_correpondencelog["sentcorrespondencemessage"]) if _correpondencelog['sentcorrespondencemessage'] not in [None,''] else None
                correpondencelog ={
                    "applicantcorrespondenceid":_correpondencelog['applicantcorrespondenceid'],
                    "parentapplicantcorrespondenceid":_correpondencelog['parentapplicantcorrespondenceid'],
                    "templateid":_correpondencelog['templateid'],
                    "text": _sentcorrespondencemessagejson['message'] if _sentcorrespondencemessagejson is not None else self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml') ,
                    "id": self.__getvaluefromjson(_correspondencemessagejson, 'id') if _isjson else None,
                    "type": self.__getvaluefromjson(_correspondencemessagejson, 'type') if _isjson else None,
                    "created_at":_correpondencelog['sent_at'] if _sentcorrespondencemessagejson is not None else _correpondencelog['created_at'],
                    "createdby":_correpondencelog['sentby'] if  _sentcorrespondencemessagejson is not None else _correpondencelog['createdby'],
                    "date": self.__pstformat(_correpondencelog['sent_at']) if _sentcorrespondencemessagejson is not None else self.__pstformat(_correpondencelog['created_at']),
                    "userId":_correpondencelog['sentby'] if _sentcorrespondencemessagejson is not None else _correpondencelog['createdby'],
                    "attachments" : attachments
                }
                correspondencelogs.append(correpondencelog)
        return correspondencelogs

    def saveapplicantcorrespondencelog(self, data, ministryrequestid, userid):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.templateid = data['templateid']
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.correspondencemessagejson = data['correspondencemessagejson']
        applicantcorrespondencelog.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        applicantcorrespondencelog.createdby = userid
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog,data['attachments'])

    def updateapplicantcorrespondencelog(self, correspondenceid, content):
        return FOIApplicantCorrespondence.updatesentcorrespondence(correspondenceid, content)
    
    def getapplicantcorrespondencelogbyid(self, applicantcorrespondenceid):
        applicantcorrespondence =  FOIApplicantCorrespondence.getapplicantcorrespondencebyid(applicantcorrespondenceid)
        (_correspondencemessagejson, _isjson) = self.__getjsonobject(applicantcorrespondence["correspondencemessagejson"])
        parser = HTMLParser()
        emailhtml_decoded_string = parser.unescape(self.__getvaluefromjson(_correspondencemessagejson, 'emailhtml')) 
        return emailhtml_decoded_string if _isjson else _correspondencemessagejson

    def getlatestapplicantcorrespondence(self, ministryid):
        return FOIApplicantCorrespondence().getlatestapplicantcorrespondence(ministryid)

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