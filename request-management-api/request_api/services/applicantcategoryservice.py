from request_api.models.ApplicantCategories import ApplicantCategory

class applicantcategoryservice:

    def getapplicantcategories():
        return ApplicantCategory.getapplicantcategories()