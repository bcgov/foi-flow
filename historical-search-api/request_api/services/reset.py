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
"""Service for reset test data."""
from typing import Dict


from request_api.models import db
from request_api.services.keycloak import KeycloakService
from request_api.utils.roles import Role


class ResetTestData:  # pylint:disable=too-few-public-methods
    """Cleanup all the data from model by created_by column."""

    def __init__(self):
        """Return a reset test data service instance."""


        
        
