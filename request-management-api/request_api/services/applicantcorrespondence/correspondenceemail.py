from request_api.models.FOICorrespondenceEmails import FOICorrespondenceEmail
from request_api.models.FOICorrespondenceEmailsRawRequests import FOICorrespondenceEmailRawRequest
from request_api.models.FOIApplicantCorrespondenceEmailsRawRequests import FOIApplicantCorrespondenceEmailRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest

import maya
import json
import html
from datetime import datetime
class correspondenceemailservice:

    def savecorrespondenceemail(self, ministryrequestid, rawrequestid, data, userid):
        """ Saves the email against the request information
        """
        if rawrequestid != 'None':
            correspondenceemail = FOICorrespondenceEmailRawRequest()
            correspondenceemail.email = data['email']
            correspondenceemail.foirawrequest_id = rawrequestid
            correspondenceemail.foirawrequestversion_id =FOIRawRequest.getversionforrequest(requestid=rawrequestid)
            correspondenceemail.createdby = userid
            correspondenceemail.created_at = datetime.now()
            return FOICorrespondenceEmailRawRequest.savecorrespondenceemail(correspondenceemail)
        else:
            correspondenceemail = FOICorrespondenceEmail()
            correspondenceemail.email = data['email']
            correspondenceemail.foiministryrequest_id = ministryrequestid
            correspondenceemail.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
            correspondenceemail.createdby = userid
            correspondenceemail.created_at = datetime.now()
            return FOICorrespondenceEmail.savecorrespondenceemail(correspondenceemail)
    

    def getcorrespondenceemails(self, ministryrequestid, rawrequestid):
        """ Saves the email against the request information
        """
        correspondenceemails = FOICorrespondenceEmailRawRequest.getcorrespondenceemails(rawrequestid)
        if ministryrequestid != 'None':
            correspondenceemails.extend(FOICorrespondenceEmail.getcorrespondenceemails(ministryrequestid))
        
        return correspondenceemails
    