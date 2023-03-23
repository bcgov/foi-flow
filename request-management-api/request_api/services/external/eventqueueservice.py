import os
from walrus import Database
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
import logging

class eventqueueservice:
    """This class is reserved for integration with event queue (currently redis streams).
    """
    host = os.getenv('EVENT_QUEUE_HOST')
    port = os.getenv('EVENT_QUEUE_PORT')
    password = os.getenv('EVENT_QUEUE_PASSWORD')

    db = Database(host=host, port=port, db=0,password=password)

    def add(self, streamkey, payload):
        try:
            stream = self.db.Stream(streamkey)
            msgid = stream.add(payload, id="*")
            return DefaultMethodResult(True,'Added to stream',msgid.decode('utf-8'))
        except Exception as err:
            logging.error("Error in contacting Redis Stream")
            logging.error(err)