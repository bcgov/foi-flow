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
"""Enum definitions."""
from enum import Enum


class RequestType(Enum):
    """Authorization header types."""

    PERSONAL = 'Personal'
    GENERAL = 'General'


class ContentType(Enum):
    """Http Content Types."""

    JSON = 'application/json'
    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    PDF = 'application/pdf'


class MinistryTeamWithKeycloackGroup(Enum):
    AEST = "AEST Ministry Team"
    AFF = "AFF Ministry Team"
    BRD = "BRD Ministry Team"
    CAS = "CAS Ministry Team"
    MCF = "MCF Ministry Team"
    CLB = "CLB Ministry Team"
    CITZ = "CITZ Ministry Team"
    EAO = "EAO Ministry Team"
    EDUC = "EDUC Ministry Team"
    EMBC = "EMBC Ministry Team"
    EMLI = "EMLI Ministry Team"
    FIN = "FIN Ministry Team"
    FLNR = "FLNR Ministry Team"
    GCPE = "GCPE Ministry Team"
    HLTH = "HLTH Ministry Team"
    IIO = "IIO Ministry Team"
    IRR = "IRR Ministry Team"
    JERI = "IRR Ministry Team"
    LBR = "LBR Ministry Team"
    LDB = "LDB Ministry Team"
    AG = "AG Ministry Team"
    MGC = "MGC Ministry Team"
    MMHA = "MMHA Ministry Team"
    MUNI = "MUNI Ministry Team"
    ENV = "ENV Ministry Team"
    SDPR = "SDPR Ministry Team"
    OBC = "OBC Ministry Team"
    OCC = "OCC Ministry Team"
    PREM = "PREM Ministry Team"
    PSA = "PSA Ministry Team"
    PSSG = "PSSG Ministry Team"
    TACS = "TACS Ministry Team"
    TIC = "TIC Ministry Team"
    TRAN = "TRAN Ministry Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, MinistryTeamWithKeycloackGroup))

class UserGroup(Enum):
    intake = "Intake Team"    
    flex = "Flex Team"
    processing = "Processing Team"
    ministry = "@bcgovcode Ministry Team" 
    
class FOIStatus(Enum):
    