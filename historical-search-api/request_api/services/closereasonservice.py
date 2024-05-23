from request_api.models.CloseReasons import CloseReason

class closereasonservice:

    def getclosereasons(self):
        """ Returns the active records
        """
        return CloseReason.getallclosereasons()