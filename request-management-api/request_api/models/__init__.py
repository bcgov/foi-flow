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

"""This exports all of the models and schemas used by the application."""
# noqa: I004
# noqa: I001, I003, I004
#from sbc_common_components.tracing.db_tracing import DBTracing  # noqa: I001, I004
#from sqlalchemy import event  # noqa: I001
#from sqlalchemy.engine import Engine  # noqa: I001, I003, I004


from .db import db, ma

from .FOIRawRequests import FOIRawRequest
from .ProgramAreas import ProgramArea
from .ApplicantCategories import ApplicantCategory
from .DeliveryModes import DeliveryMode
from .ReceivedModes import ReceivedMode

from .FOIRequests import FOIRequest
from .FOIRequestStatus import FOIRequestStatus
from .FOIMinistryRequests import FOIMinistryRequest

from .ContactTypes import ContactType
from .FOIRequestContactInformation import FOIRequestContactInformation

from .RequestorType import RequestorType
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestApplicantMappings import FOIRequestApplicantMapping

from .PersonalInformationAttributes import PersonalInformationAttribute

from .FOIRequestPersonalAttributes import FOIRequestPersonalAttribute

from .RevenueAccount import RevenueAccount
from .FeeCode import FeeCode
from .Payment import Payment
from .DocumentType import DocumentType
from .DocumentTemplate import DocumentTemplate

from .FOIRequestExtensions import FOIRequestExtension
from .FOIAssignees import FOIAssignee

from .ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate

#event.listen(Engine, 'before_cursor_execute', DBTracing.query_tracing)
