from request_api.models.CloseReasons import CloseReason

class closereasonservice:

    def getclosereasons(self):
        """ Returns the active records
        """
        return CloseReason.getallclosereasons()
    
    @staticmethod
    def getclosereason(closereasonid):
        """ Returns a specific close reason by ID """
        return CloseReason.getclosereason(closereasonid)