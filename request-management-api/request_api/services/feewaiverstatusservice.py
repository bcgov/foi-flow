from request_api.models.FeeWaiverStatus import FeeWaiverStatus

class feewaiverstatusservice:

    def getfeewaiverstatuses(self):
        """ Returns the active records
        """
        return FeeWaiverStatus().getallwaiverstatuses()

    def getfeewaiverstatusidbyname(self, status):
        """ Returns the active records
        """
        return FeeWaiverStatus().getwaiverstatusid(status)['waiverstatusid']