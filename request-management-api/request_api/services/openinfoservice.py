from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIOpenInfoAdditionalFiles import FOIOpenInfoAdditionalFiles
from datetime import datetime

class openinfoservice:
    """ OpenInformation service
    This service class manages all CRUD operations related to open information
    """
    def getopeninfostatuses (self):
        return OpenInformationStatuses.getallstatuses()

    def getopeninfopublicationstatuses (self):
        return OpenInfoPublicationStatuses.getallpublicationstatuses()

    def getopeninfoexemptions (self):
        return OpenInformationExemptions.getallexemptions()
    
    def getcurrentfoiopeninforequest(self, foiministryrequestid):
       return FOIOpenInformationRequests().getcurrentfoiopeninforequest(foiministryrequestid)
    
    def createopeninforequest(self, foiopeninforequest, userid, foiministryrequestid):
        version = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        foiopeninforequest['foiministryrequestversion_id'] = version
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        result = FOIOpenInformationRequests().createopeninfo(foiopeninforequest, userid)
        return result

    def updateopeninforequest(self, foiopeninforequest, userid, foiministryrequestid):
        prev_foiopeninforequest = self.getcurrentfoiopeninforequest(foiministryrequestid)
        foiministryrequestversion = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        foiopeninforequest['foiministryrequestversion_id'] = foiministryrequestversion
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        foiopeninforequest['version'] = prev_foiopeninforequest["version"]
        foiopeninforequest["created_at"] = prev_foiopeninforequest["created_at"]
        foiopeninforequest["createdby"] = prev_foiopeninforequest["createdby"]
        foiopeninforequest['processingstatus'] = prev_foiopeninforequest["processingstatus"]
        foiopeninforequest["processingmessage"] = prev_foiopeninforequest["processingmessage"]
        foiopeninforequest["sitemap_pages"] = prev_foiopeninforequest["sitemap_pages"]
        result = FOIOpenInformationRequests().updateopeninfo(foiopeninforequest, userid)
        deactivateresult = None
        if result.success == True:
            foiopeninfoid = result.identifier
            deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
        if result and deactivateresult:
            return result            
    
    def fetchopeninfoadditionalfiles(self, foiministryrequestid):
        return FOIOpenInfoAdditionalFiles.fetch(foiministryrequestid)
    
    def saveopeninfoadditionalfiles(self, foiministryrequestid, files, userid):
        filelist = []
        for file in files['additionalfiles']:
            _file = FOIOpenInfoAdditionalFiles(ministryrequestid=foiministryrequestid, createdby = userid, created_at = datetime.now(), isactive=True)
            _file.__dict__.update(file)
            filelist.append(_file)
        filesaveresult = FOIOpenInfoAdditionalFiles.create(filelist)
        return filesaveresult
    
    def deleteopeninfoadditionalfiles(self, fileids, userid):
        return FOIOpenInfoAdditionalFiles.bulkdelete(fileids['fileids'], userid)
