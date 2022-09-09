from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
from request_api.models.FOIApplicantCorrespondences import FOIApplicantCorrespondence
class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active applicant correspondence templates
        """
        return ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()

    def saveapplicantcorrespondencelog(self,templateid,ministryrequestid,createdby,messagehtml):
        applicantcorrespondencelog = FOIApplicantCorrespondence()
        applicantcorrespondencelog.templateid = templateid
        applicantcorrespondencelog.foiministryrequest_id = ministryrequestid
        applicantcorrespondencelog.correspondencemessagejson = messagehtml
        #GET MINISTRY REQUEST and update version below
        applicantcorrespondencelog.foiministryrequestversion = 1 
        applicantcorrespondencelog.createdby = createdby
        return FOIApplicantCorrespondence.saveapplicantcorrespondence(applicantcorrespondencelog)
