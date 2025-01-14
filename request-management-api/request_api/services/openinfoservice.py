from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIOpenInfoAdditionalFiles import FOIOpenInfoAdditionalFiles
from request_api.models.FOIAssignees import FOIAssignee
from request_api.services.events.openinfo import openinfoevent
from request_api.schemas.foiopeninfo import FOIOpenInfoSchema
from request_api.utils.constants import SKIP_OPENINFO_MINISTRIES
from request_api.utils.enums import OpenInfoNotificationType        
from request_api.auth import AuthHelper
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
    
    def createopeninforequest(self, foirequestschema, userid, foiministryrequest):
        foiministryrequestid = foiministryrequest.foiministryrequestid
        current_oirequest = self.getcurrentfoiopeninforequest(foiministryrequestid)
        if foirequestschema["requestType"] == 'general' and foirequestschema["selectedMinistries"][0]["code"].upper() not in SKIP_OPENINFO_MINISTRIES and current_oirequest == {}:
            default_foiopeninforequest = {
                "oipublicationstatus_id": 2,
            }
            foiopeninforequest = FOIOpenInfoSchema().load(default_foiopeninforequest)
            version = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
            foiopeninforequest['foiministryrequestversion_id'] = version
            foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
            result = FOIOpenInformationRequests().createopeninfo(foiopeninforequest, userid)
            return result

    def updateopeninforequest(self, foiopeninforequest, userid, foiministryrequestid, assigneedetails):
        is_new_assignment = False
        if 'oiassignedto' in foiopeninforequest:
            current_request = self.getcurrentfoiopeninforequest(foiministryrequestid)
            is_new_assignment = current_request and current_request.get('oiassignedto') is None and foiopeninforequest['oiassignedto'] is not None
            is_assignment_changed = current_request and current_request.get('oiassignedto') != foiopeninforequest['oiassignedto']
            self.updateopeninfoassignee(foiopeninforequest['oiassignedto'], assigneedetails)

        foiministryrequestversion = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        foiopeninforequest['foiministryrequestversion_id'] = foiministryrequestversion
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        result = FOIOpenInformationRequests().saveopeninfo(foiopeninforequest, userid)

        if result.success == True:
            foiministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
            requestid = foiministryrequest['foirequest_id'] if foiministryrequest else None
            if is_new_assignment:
                # Clear OI Team notifications
                openinfoevent().dismiss_exemption_notifications(foiministryrequestid)
            if is_assignment_changed:
                openinfoevent().createopeninfoassigneeevent(foiministryrequestid, requestid, AuthHelper.getuserid(), AuthHelper.getusername(), assigneedetails)
            
            # Handle exemption decision notifications
            if 'oiexemptionapproved' in foiopeninforequest and foiopeninforequest['oiexemptionapproved'] is not None:
                notification_type = OpenInfoNotificationType.EXEMPTION_APPROVED.value if foiopeninforequest['oiexemptionapproved'] is True else OpenInfoNotificationType.EXEMPTION_DENIED.value                
                oiexemption_id = foiopeninforequest['oiexemption_id'] if foiopeninforequest['oiexemption_id'] else None
                openinfoevent().handle_exemption_request(foiministryrequestid, requestid, AuthHelper.getuserid(), AuthHelper.getusername(), notification_type, oiexemption_id)

            if result.message != 'FOIOpenInfo request created':
                foiopeninfoid = result.identifier
                deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
                if deactivateresult.success:
                    return result
            return result
        else:
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
        result = FOIOpenInformationRequests().saveopeninfo(foiopeninforequest, userid)
        deactivateresult = None
        if result.success == True:
            foiopeninfoid = result.identifier
            deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
        if result and deactivateresult:
            return result