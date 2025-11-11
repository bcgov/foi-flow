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
    AGR = "AGR Ministry Team"
    AG = "AG Ministry Team"
    BRD = "BRD Ministry Team"
    CAS = "CAS Ministry Team"
    CAF = "CAF Ministry Team"
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
    LSB = "LSB Ministry Team"
    INF = "INF Ministry Team"
    MCM = "MCM Ministry Team"
    ECS = "ECS Ministry Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, MinistryTeamWithKeycloackGroup))

class ProcessingTeamWithKeycloackGroup(Enum):
    scanningteam = "Scanning Team"
    centralteam = "Central Team"
    justicehealthteam = "Justice Health Team"
    mcfdpersonalteam = "MCFD Personals Team"
    socialtechteam = "Social Education"
    infrastructureteam = "Infrastructure Team"
    resourceteam = "Resource Team"
    communityhealthteam = "Community and Health Team"
    childrenfamilyteam = "Children and Family Team"
    childreneducationteam = "Children and Education Team"
    justiceteam = "Justice Team"
    bcpsteam = "BCPS Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, ProcessingTeamWithKeycloackGroup))

class IAOTeamWithKeycloackGroup(Enum):
    intake = "Intake Team"
    flex = "Flex Team"
    oi = "OI Team"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, IAOTeamWithKeycloackGroup)) + list(map(lambda c: c.value, ProcessingTeamWithKeycloackGroup))

class UserGroup(Enum):
    intake = "Intake Team"
    flex = "Flex Team"
    processing = "@processing"
    ministry = "@bcgovcode Ministry Team"
    oi = "OI Team"

class RequestorType(Enum):
    applicant = 1
    onbehalfof = 2
    child = 3

class FeeType(Enum):
    application = 'FOI0001'
    processing = 'FOI0002'

class PaymentEventType(Enum):
    paid = "PAID"    
    expired = "EXPIRED"
    outstandingpaid = "OUTSTANDINGPAID"
    depositpaid = "DEPOSITPAID"
    reminder = "REMINDER"

class CommentType(Enum):
    """Authorization header types."""
    UserComment = 1
    SystemGenerated = 2
    DivisionStages = 3

class DocumentPathMapperCategory(Enum):
    Attachments = "Attachments"
    Records = "Records"
    Historical = "Historical"
    AdditionalFiles = "AdditionalFiles"

class ServiceName(Enum):
    payonline = "payonline"
    payoutstanding = "payoutstanding"
    correspondence = "correspondence"

class StateName(Enum):
    open = "Open"
    callforrecords = "Call For Records"
    closed = "Closed"
    redirect = "Redirect"
    unopened = "Unopened"
    intakeinprogress = "Intake in Progress"
    consult = "Consult"
    ministrysignoff = "Ministry Sign Off"
    onhold = "On Hold"
    deduplication = "Deduplication"
    harmsassessment = "Harms Assessment"    
    response = "Response"
    feeestimate = "Fee Estimate"
    recordsreview = "Records Review"
    recordsreadyforreview = "Records Ready for Review"
    archived = "Archived"
    peerreview = "Peer Review"
    tagging = "Tagging"
    readytoscan = "Ready to Scan"
    appfeeowing = "App Fee Owing"
    section5pending = "Section 5 Pending"
    onholdother = "On Hold - Other"
class CacheUrls(Enum):
    keycloakusers= "/api/foiassignees"
    programareas= "/api/foiflow/programareas"
    deliverymodes= "/api/foiflow/deliverymodes"
    receivedmodes= "/api/foiflow/receivedmodes"
    closereasons= "/api/foiflow/closereasons"
    extensionreasons= "/api/foiflow/extensionreasons"
    applicantcategories= "/api/foiflow/applicantcategories"
    subjectcodes= "/api/foiflow/subjectcodes"


class ExcludedProgramArea(Enum):
    """Program areas to exclude from OI requests."""
    CLB = 24
    IIO = 29
    TIC = 32
    OBC = 33
    MGC = 34

    @staticmethod
    def list():
        return [area.value for area in ExcludedProgramArea]

class OICloseReason(Enum):
    """Open Information eligible close reasons."""
    FULL_DISCLOSURE = 4
    PARTIAL_DISCLOSURE = 7

    @staticmethod
    def list():
        return [reason.value for reason in OICloseReason]

class OIStatusEnum(Enum):
    FIRST_REVIEW = 1
    PEER_REVIEW = 2
    READY_TO_PUBLISH = 3
    PUBLISHED = 4
    HOLD_PUBLICATION = 5
    UNPUBLISHED = 6
    DO_NOT_PUBLISH = 7
    EXEMPTION_REQUEST = 8

    @classmethod
    def list(cls):
        return [status.value for status in cls]

class OpenInfoNotificationType(Enum):
    EXEMPTION_REQUEST = "Exemption Request"
    EXEMPTION_APPROVED = "Exemption Approved"
    EXEMPTION_DENIED = "Exemption Denied"
    OI_STATE = "OI State"
    OI_ASSIGNEE = "OI Assignee"

    @staticmethod
    def list():
        return [notification.value for notification in OpenInfoNotificationType]