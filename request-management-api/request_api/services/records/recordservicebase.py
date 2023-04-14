from os import stat, path,getenv
from re import VERBOSE
from request_api.utils.constants import FILE_CONVERSION_FILE_TYPES, DEDUPE_FILE_TYPES, NONREDACTABLE_FILE_TYPES
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.models.default_method_result import DefaultMethodResult
from request_api.auth import auth, AuthHelper
import json
from datetime import datetime
import maya
import uuid
import requests
import logging

class recordservicebase:
    """ This class consolidates retrival of FOI Records for actors: iao and ministry. 
    """
    docreviewerapiurl =  getenv("FOI_DOCREVIEWER_BASE_API_URL")
    docreviewerapitimeout =  getenv("FOI_DOCREVIEWER_BASE_API_TIMEOUT")

    def makedocreviewerrequest(self, method, url, payload=None):
        token = AuthHelper.getauthtoken()
        try:
            response = requests.request(
                method=method,
                url=self.docreviewerapiurl+url,
                data=json.dumps(payload),
                headers={'Authorization': token, 'Content-Type': 'application/json'},
                timeout=float(self.docreviewerapitimeout)
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.HTTPError as err:
            logging.error("Doc Reviewer API returned the following message: {0} - {1}".format(err.response.status_code, err.response.text))
            return None, err
        except requests.exceptions.RequestException as err:
            logging.error(err)
            return None, err
        
    def isvalid(self, property, dict):
        if property in dict and dict[property] is not None:
            return True
        return False