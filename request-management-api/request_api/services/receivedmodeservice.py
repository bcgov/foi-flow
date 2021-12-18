from request_api.models.ReceivedModes import ReceivedMode

class receivedmodeservice:

    def getreceivedmodes():
        return ReceivedMode.getreceivedmodes()