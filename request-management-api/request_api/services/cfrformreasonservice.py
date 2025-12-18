from request_api.models.CFRFormReason import CFRFormReason

class cfrformreasonservice:

    def getcfrformreasons(self):
        """ Returns the active records
        """
        return CFRFormReason().getallcfrformreasons()
    
    def getcfrformreasonidbyname(self, reason):
        """ Returns the active records
        """
        return CFRFormReason().getcfrformreasonid(reason)['cfrformreasonid']