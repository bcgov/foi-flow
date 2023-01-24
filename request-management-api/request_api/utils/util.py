# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CORS pre-flight decorator.

A simple decorator to add the options method to a Request Class.
"""

import base64
import re
import urllib
from functools import wraps

from humps.main import camelize, decamelize
from flask import request, g
from sqlalchemy.sql.expression import false
from request_api.auth import jwt as _authjwt,AuthHelper
import jwt
import os
from request_api.utils.enums import MinistryTeamWithKeycloackGroup, ProcessingTeamWithKeycloackGroup
from request_api.services.rawrequestservice import rawrequestservice
from request_api.models.FOIRequestWatchers import  FOIRequestWatcher


def cors_preflight(methods):
   #Render an option method on the class.

    def wrapper(f):
        def options(self, *args, **kwargs):  # pylint: disable=unused-argument
            return {'Allow': 'GET, DELETE, PUT, POST'}, 200, \
                   {
                    #'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': methods,
                    'Access-Control-Allow-Headers': 'Authorization, Content-Type, registries-trace-id, '
                                                    'invitation_token'}

        setattr(f, 'options', options)
        return f

    return wrapper


def camelback2snake(camel_dict: dict):
    """Convert the passed dictionary's keys from camelBack case to snake_case."""
    return decamelize(camel_dict)


def snake2camelback(snake_dict: dict):
    """Convert the passed dictionary's keys from snake_case to camelBack case."""
    return camelize(snake_dict)

def getrequiredmemberships():
    membership =''
    for group in MinistryTeamWithKeycloackGroup:
        membership+='{0},'.format(group.value)
    for procgroup in ProcessingTeamWithKeycloackGroup:
        membership+='{0},'.format(procgroup.value)
    membership+='Intake Team,Flex Team'   
    return membership

def allowedorigins():
    _allowedcors = os.getenv('CORS_ORIGIN')
    allowedcors = []
    if ',' in _allowedcors:
        for entry in re.split(",",_allowedcors):
            allowedcors.append(entry)
    return allowedcors

class Singleton(type):
    """Singleton meta."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call for meta."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def digitify(payload: str) -> int:
    """Return the digits from the string."""
    return int(re.sub(r'\D', '', payload))


def escape_wam_friendly_url(param):
    """Return encoded/escaped url."""
    base64_org_name = base64.b64encode(bytes(param, encoding='utf-8')).decode('utf-8')
    encode_org_name = urllib.parse.quote(base64_org_name, safe='')
    return encode_org_name

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was    

def canrestictdata(requestid,assignee,isrestricted,israwrequest):

    _isawatcher = False
    currentuser = AuthHelper.getuserid()
    if israwrequest :
        _isawatcher = rawrequestservice().israwrequestwatcher(requestid,currentuser)
    else:
        _isawatcher = FOIRequestWatcher.isaiaoministryrequestwatcher(requestid,currentuser)

    isiaorestrictedfilemanager = AuthHelper.isiaorestrictedfilemanager()
    # print('Current user is {0} , is a watcher: {1} and is file manager {2} '.format(currentuser,_isawatcher,isiaorestrictedfilemanager))
    if(isrestricted and currentuser != assignee and _isawatcher == False and isiaorestrictedfilemanager == False):
        return True
    else:
        return False    

        


