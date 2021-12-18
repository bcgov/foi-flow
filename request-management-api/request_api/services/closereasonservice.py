from request_api.models.CloseReasons import CloseReason

class closereasonservice:

    def getclosereasons():
        return CloseReason.getallclosereasons()