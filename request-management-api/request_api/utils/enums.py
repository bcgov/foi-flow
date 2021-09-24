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
    AEST = "AED Ministry Team"
    AFF = "AGR Ministry Team"
    BRD = "BRD Ministry Team"
    CAS = "CAS Ministry Team"
    MCF = "CFD Ministry Team"
    CLB = "CLB Ministry Team"
    CITZ = "CTZ Ministry Team"
    EAO = "EAO Ministry Team"
    EDUC = "EDU Ministry Team"
    EMBC = "EMB Ministry Team"
    EMLI = "EML Ministry Team"
    FIN = "FIN Ministry Team"
    FLNR = "FNR Ministry Team"
    GCPE = "GCP Ministry Team"
    HLTH = "HLTH Ministry Team"
    IIO = "IIO Ministry Team"
    IRR = "IRR Ministry Team"
    JERI = "JER Ministry Team"
    LBR = "LBR Ministry Team"
    LDB = "LDB Ministry Team"
    AG = "MAG Ministry Team"
    MGC = "MGC Ministry Team"
    MMHA = "MHA Ministry Team"
    MUNI = "MMA Ministry Team"
    ENV = "MOE Ministry Team"
    SDPR = "MSD Ministry Team"
    OBC = "OBC Ministry Team"
    OCC = "OCC Ministry Team"
    PREM = "OOP Ministry Team"
    PSA = "PSA Ministry Team"
    PSSG = "PSS Ministry Team"
    TACS = "TAC Ministry Team"
    TIC = "TIC Ministry Team"
    TRAN = "TRA Ministry Team"

