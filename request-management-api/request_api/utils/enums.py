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
    AED = "AED Ministry Team"
    AGR = "AGR Ministry Team"
    BRD = "BRD Ministry Team"
    CAS = "CAS Ministry Team"
    CFD = "CFD Ministry Team"
    CLB = "CLB Ministry Team"
    CTZ = "CTZ Ministry Team"
    EAO = "EAO Ministry Team"
    EDU = "EDU Ministry Team"
    EMB = "EMB Ministry Team"
    EML = "EML Ministry Team"
    FIN = "FIN Ministry Team"
    FNR = "FNR Ministry Team"
    GCP = "GCP Ministry Team"
    HLTH = "HLTH Ministry Team"
    IIO = "IIO Ministry Team"
    IRR = "IRR Ministry Team"
    JER = "JER Ministry Team"
    LBR = "LBR Ministry Team"
    LDB = "LDB Ministry Team"
    MAG = "MAG Ministry Team"
    MGC = "MGC Ministry Team"
    MHA = "MHA Ministry Team"
    MMA = "MMA Ministry Team"
    MOE = "MOE Ministry Team"
    MSD = "MSD Ministry Team"
    OBC = "OBC Ministry Team"
    OCC = "OCC Ministry Team"
    OOP = "OOP Ministry Team"
    PSA = "PSA Ministry Team"
    PSS = "PSS Ministry Team"
    TAC = "TAC Ministry Team"
    TIC = "TIC Ministry Team"
    TRA = "TRA Ministry Team"
    
