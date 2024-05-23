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
import requests
import logging
from os import getenv
"""Constants definitions."""

# Group names

FORMAT_CONTACT_ADDRESS='JSON'
BLANK_EXCEPTION_MESSAGE = 'Field cannot be blank'
MAX_EXCEPTION_MESSAGE = 'Field exceeds the size limit'
FILE_CONVERSION_FILE_TYPES = ''
DEDUPE_FILE_TYPES = ''
NONREDACTABLE_FILE_TYPES = ''
try:
    response = requests.request(
        method='GET',
        url=getenv("FOI_RECORD_FORMATS"),
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    response.raise_for_status()
    FILE_CONVERSION_FILE_TYPES = response.json()['conversion']
    DEDUPE_FILE_TYPES = response.json()['dedupe']
    NONREDACTABLE_FILE_TYPES = response.json()['nonredactable']
except Exception as err:
    logging.error("Unable to retrieve record upload formats from S3")
    logging.error(err)


