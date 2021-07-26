from request_api.models.DeliveryModes import DeliveryMode

class deliverymodeservice:

    def getdeliverymodes():
        return DeliveryMode.getdeliverymodes()