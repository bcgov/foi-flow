# models\defaultMethodResult.py
class DefaultMethodResult():
    success: False
    message: ''
    identifier:''
    def __init__(self, success, message,identifier):
        self.success = success
        self.message = message
        self.identifier=identifier