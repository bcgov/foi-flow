from request_api.models.FOICorrespondenceEmails import FOICorrespondenceEmail
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

import maya
import json
import html
from datetime import datetime
class correspondenceemailservice:

    def savecorrespondenceemail(self, ministryrequestid, data, userid):
        """ Saves the email against the request information
        """
        correspondenceemail = FOICorrespondenceEmail()
        correspondenceemail.email = data['email']
        correspondenceemail.foiministryrequest_id = ministryrequestid
        correspondenceemail.foiministryrequestversion_id =FOIMinistryRequest.getversionforrequest(ministryrequestid=ministryrequestid)
        correspondenceemail.createdby = userid
        correspondenceemail.created_at = datetime.now()
        return FOICorrespondenceEmail.savecorrespondenceemail(correspondenceemail)
    

    def getcorrespondenceemails(self, ministryrequestid):
        """ Saves the email against the request information
        """
        correspondenceemails = FOICorrespondenceEmail.getcorrespondenceemails(ministryrequestid)
        
        return correspondenceemails
    