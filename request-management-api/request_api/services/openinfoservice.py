from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIOpenInfoAdditionalFiles import FOIOpenInfoAdditionalFiles
from request_api.models.FOIAssignees import FOIAssignee
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

    def updateopeninforequest(self, foiopeninforequest, userid, foiministryrequestid, assigneedetails):
        # Handle assignee update
        if 'oiassignedto' in foiopeninforequest:
            self.updateopeninfoassignee(foiopeninforequest['oiassignedto'], assigneedetails)
        
        prev_foiopeninforequest = self.getcurrentfoiopeninforequest(foiministryrequestid)
        foiministryrequestversion = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        foiopeninforequest['foiministryrequestversion_id'] = foiministryrequestversion
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        foiopeninforequest['version'] = prev_foiopeninforequest["version"]
        foiopeninforequest['foiopeninforequestid'] = prev_foiopeninforequest["foiopeninforequestid"]
        result = FOIOpenInformationRequests().updateopeninfo(foiopeninforequest, userid)
        deactivateresult = None
        if result.success == True:
            foiopeninfoid = result.identifier
            deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
        if result and deactivateresult:
            return result     

    def updateopeninfoassignee(self, assignee, assigneedetails):
        if not assignee or not assigneedetails:
            return
        
        # Get assignee info from FOIAssignee table    
        existing_assignee = FOIAssignee.query.filter_by(username=assignee).first()
        if not existing_assignee and assigneedetails:
            FOIAssignee.saveassignee(
                assignee,
                assigneedetails.get('assignedToFirstName', ''),
                '',
                assigneedetails.get('assignedToLastName', '')
            )
        return assignee
    
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
    
    def updatefoioirequest_onfoirequestchange(self, foiministryrequestid, new_foirequestversion, userid):
        foiopeninforequest = self.getcurrentfoiopeninforequest(foiministryrequestid)
        foiopeninforequest['foiministryrequestversion_id'] = new_foirequestversion
        result = FOIOpenInformationRequests().updateopeninfo(foiopeninforequest, userid)
        deactivateresult = None
        if result.success == True:
            foiopeninfoid = result.identifier
            deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
        if result and deactivateresult:
            return result