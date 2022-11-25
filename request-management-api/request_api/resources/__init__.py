# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exposes all of the resource endpoints mounted in Flask-Blueprint style.

Uses restplus namespaces to mount individual api endpoints into the service.

All services have 2 defaults sets of endpoints:
 - ops
 - meta
That are used to expose operational health information about the service, and meta information.
"""

from flask import Blueprint

from .apihelper import Api

from .meta import API as META_API
from .ops import API as OPS_API
from .request import API as REQUEST_API
from .foirequest import API as FOIREQUEST_API
from .foiflowmasterdata import API as FOIFLOWMASTERDATA_API
from .dashboardpagination import API as DASHBOARDPAGINATION_API
from .advancedsearch import API as ADVANCEDSEARCH_API
from .foiassignee import API as FOIASSIGNEE_API
from .foiaudit import API as FOIAUDTI_API
from .foiwatcher import API as FOIWATCHER_API
from .foicomment import API as FOICOMMENT_API
from .foidocument import API as FOIDOCUMENT_API
from .foiextension import API as FOIEXTENSION_API
from .fee import API as FEE_API
from .foinotification import API as FOINOTIFICATION_API
from .foicfrfee import API as FOICFRFEE_API
from .foiemail import API as FOIEMAIL_API
from .foipayment import API as FOIPAYMENT_API
from .applicantcorrespondence import API as APPLICANTCORRESPONDENCE_API
from .foiworkflow import API as FOIWORKFLOW_API

__all__ = ('API_BLUEPRINT')

# This will add the Authorize button to the swagger docs
#AUTHORIZATIONS = {'apikey': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}}


API_BLUEPRINT = Blueprint('API', __name__ )


API = Api(
    API_BLUEPRINT,
    title='FOI Request API',
    version='1.0',
    description='The Core API for the FOI Request System',
)



API.add_namespace(META_API, path="/api")
API.add_namespace(OPS_API ,path="/api")
API.add_namespace(REQUEST_API ,path="/api")
API.add_namespace(FOIREQUEST_API ,path="/api")
API.add_namespace(FOIFLOWMASTERDATA_API ,path="/api")
API.add_namespace(DASHBOARDPAGINATION_API,'/api')
API.add_namespace(ADVANCEDSEARCH_API, '/api')
API.add_namespace(FOIASSIGNEE_API,'/api')
API.add_namespace(FOIAUDTI_API,'/api')
API.add_namespace(FOIWATCHER_API,'/api')
API.add_namespace(FOICOMMENT_API,'/api')
API.add_namespace(FOIDOCUMENT_API,'/api')
API.add_namespace(FOIEXTENSION_API,'/api')
API.add_namespace(FEE_API,'/api')
API.add_namespace(FOINOTIFICATION_API,'/api')
API.add_namespace(FOICFRFEE_API, '/api')
API.add_namespace(FOIEMAIL_API, '/api')
API.add_namespace(FOIPAYMENT_API, '/api')
API.add_namespace(APPLICANTCORRESPONDENCE_API, '/api')
API.add_namespace(FOIWORKFLOW_API, '/api')