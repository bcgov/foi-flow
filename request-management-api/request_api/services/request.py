
from typing import Dict

from flask import current_app
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

class Request:
    """ FOI Request management service
    
    This service class manages all CRUD operations related to an FOI Request
    
    """

    def __init__(self, model):
        self._model = model

   
