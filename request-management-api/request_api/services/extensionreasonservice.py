from request_api.models.ExtensionReasons import ExtensionReason

class extensionreasonservice:

    def getextensionreasons(self):
        """ Returns the active records
        """
        return ExtensionReason().getallextensionreasons()
    
    def getextensionreasonbyid(self, extensionreasonid):
        """ Returns the active records
        """
        return ExtensionReason().getextensionreasonbyid(extensionreasonid)