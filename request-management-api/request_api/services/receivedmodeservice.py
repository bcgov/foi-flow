from request_api.models.ReceivedModes import ReceivedMode

class receivedmodeservice:

    def getreceivedmodes(self):
        """ Returns the active records
        """
        return ReceivedMode.getreceivedmodes()