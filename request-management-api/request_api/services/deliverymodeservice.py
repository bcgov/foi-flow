from request_api.models.DeliveryModes import DeliveryMode

class deliverymodeservice:

    def getdeliverymodes(self):
        """ Returns the active records
        """
        return DeliveryMode.getdeliverymodes()