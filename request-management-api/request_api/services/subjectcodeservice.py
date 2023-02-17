from request_api.models.SubjectCodes import SubjectCode
from request_api.models.FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

class subjectcodeservice:

    def getsubjectcodes(self):
        """ Returns the active records
        """
        return SubjectCode.getsubjectcodes()
    
    def getsubjectcodebyname(self, subjectcode):
        """ Returns the subject code
        """
        return SubjectCode.getsubjectcodebyname(subjectcode)

    def getsubjectcodebyid(self, subjectcodeid):
        """ Returns the subject code
        """
        return SubjectCode.getsubjectcodebyid(subjectcodeid)

    def getministrysubjectcode(self, ministryrequestid):
        """ Returns the ministry subject code
        """
        ministryrequestversion = self.__getministryversionforrequest(ministryrequestid)
        return FOIMinistryRequestSubjectCode.getministrysubjectcode(ministryrequestid, ministryrequestversion)

    def savesubjectcode(self, ministryrequestid, subjectcode, userid):
        """ Save subject code
        """
        ministryrequestversion = self.__getministryversionforrequest(ministryrequestid)
        subjectcode = self.getsubjectcodebyname(subjectcode)
        return FOIMinistryRequestSubjectCode.savesubjectcode(ministryrequestid, ministryrequestversion, subjectcode['subjectcodeid'], userid)

    def getministrysubjectcodename(self, foiministryrequestid):
        """ Returns the ministry subject code name
        """
        ministrysubjectcode = self.getministrysubjectcode(foiministryrequestid)
        if ministrysubjectcode:
            subjectcode = self.getsubjectcodebyid(ministrysubjectcode['subjectcodeid'])
            return subjectcode['name']
        else:
            return ''
    
    def __getministryversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """
        request = FOIMinistryRequest.getversionforrequest(requestid)
        if request:
            return request[0]