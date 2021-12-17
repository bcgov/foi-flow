from request_api.models.ApplicantCategories import ApplicantCategory

class applicantcategoryservice:

    def getapplicantcategories(self):
        """ Returns the active records
        """
        return ApplicantCategory.getapplicantcategories()