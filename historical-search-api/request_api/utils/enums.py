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





class MinistryTeamWithKeycloackGroup(Enum):
    AEST = "AEST Ministry Team"
    AGR = "AGR Ministry Team"
    AG = "AG Ministry Team"
    BRD = "BRD Ministry Team"
    CAS = "CAS Ministry Team"
    CITZ = "CITZ Ministry Team"
    CLB = "CLB Ministry Team"
    DAS = "DAS Ministry Team"
    EAO = "EAO Ministry Team"
    EDU = "EDU Ministry Team"
    EMBC = "EMBC Ministry Team"
    EMC = "EMC Ministry Team"
    EMLI = "EMLI Ministry Team"
    ENV = "ENV Ministry Team"
    FIN = "FIN Ministry Team"
    FOR = "FOR Ministry Team"
    GCP = "GCP Ministry Team"
    HTH = "HTH Ministry Team"
    IIO = "IIO Ministry Team"
    IRR = "IRR Ministry Team"
    JERI = "JERI Ministry Team"
    LBR = "LBR Ministry Team"
    LDB = "LDB Ministry Team"
    LWR = "LWR Ministry Team"
    WLR = "WLR Ministry Team"
    MCF = "MCF Ministry Team"
    MGC = "MGC Ministry Team"
    MMHA = "MMHA Ministry Team"
    MUNI = "MUNI Ministry Team"
    OBC = "OBC Ministry Team"
    OCC = "OCC Ministry Team"
    OOP = "OOP Ministry Team"
    PSA = "PSA Ministry Team"
    PSSG = "PSSG Ministry Team"
    MSD = "MSD Ministry Team"
    TACS = "TACS Ministry Team"
    TIC = "TIC Ministry Team"
    TRAN = "TRAN Ministry Team"
    PSE = "PSE Ministry Team"
    ECC = "ECC Ministry Team"
    JED = "JED Ministry Team"
    COR = "COR Ministry Team"
    HSG = "HSG Ministry Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, MinistryTeamWithKeycloackGroup))

class ProcessingTeamWithKeycloackGroup(Enum):
    scanningteam = "Scanning Team"
    centralteam = "Central Team"
    justicehealthteam = "Justice Health Team"
    mcfdpersonalteam = "MCFD Personals Team"
    resouceteam = "Resource Team"
    socialtechteam = "Social Education"
    centraleconteam = "Central and Economy Team"
    resourcejusticeteam = "Resource and Justice Team"
    communityhealthteam = "Community and Health Team"
    childrenfamilyteam = "Children and Family Team"
    childreneducationteam = "Children and Education Team"
    coordinatedresponseunit = "Coordinated Response Unit"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, ProcessingTeamWithKeycloackGroup))

class IAOTeamWithKeycloackGroup(Enum):
    intake = "Intake Team"
    flex = "Flex Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, IAOTeamWithKeycloackGroup)) + list(map(lambda c: c.value, ProcessingTeamWithKeycloackGroup))

class UserGroup(Enum):
    intake = "Intake Team"
    flex = "Flex Team"
    processing = "@processing"
    ministry = "@bcgovcode Ministry Team"

