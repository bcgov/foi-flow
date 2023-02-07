# models\defaultMethodResult.py
class DefaultMethodResult():
    success: False
    message: None
    identifier: None
    def __init__(self, success, message,identifier=None,*args):
        self.success = success
        self.message = message
        self.identifier=identifier
        self.args=args