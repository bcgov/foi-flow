from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate

class applicantcorrespondenceservice:

    def getapplicantcorrespondencetemplates(self):
        """ Returns the active records
        """
        return ApplicationCorrespondenceTemplate.getapplicantcorrespondencetemplates()