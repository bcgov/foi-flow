from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()

    def saveapplicantcorrespondencelog(self,templateid,ministryrequestid,createdby,messagehtml,attachments):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.templateid = templateid
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.correspondencemessagejson = messagehtml        
        applicantcorrespondencelog.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid) 
        applicantcorrespondencelog.createdby = createdby
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog,attachments)
