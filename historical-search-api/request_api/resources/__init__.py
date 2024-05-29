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

__all__ = ('API_BLUEPRINT')


API_BLUEPRINT = Blueprint('API', __name__ )


API = Api(
    API_BLUEPRINT,
    title='FOI Historical Search  API',
    version='1.0',
    description='The Historical Search  API  for the FOI Request System',
)



API.add_namespace(REQUEST_API ,path="/api")