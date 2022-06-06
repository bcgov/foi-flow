from request_api.models.CFRFeeStatus import CFRFeeStatus

class cfrfeestatusservice:

    def getcfrfeestatuses(self):
        """ Returns the active records
        """
        return CFRFeeStatus().getallcfrfeestatuses()
    
    def getcfrfeestatusidbyname(self, status):
        """ Returns the active records
        """
        return CFRFeeStatus().getcfrfeestatusid(status)['cfrfeestatusid']