from request_api.models.SubjectCodes import SubjectCode

class subjectcodeservice:

    def getsubjectcodes(self):
        """ Returns the active records
        """
        return SubjectCode.getsubjectcodes()
    
    def getsubjectcodebyname(self, subjectcode):
        """ Returns the subject code
        """
        return SubjectCode.getsubjectcodebyname(subjectcode)