# Copyright © 2019 Province of British Columbia
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


"""Service for hashing."""
import hashlib

from flask import current_app
from typing import Dict
from urllib.parse import parse_qsl


class HashService:
    """Hash Service class."""

    @staticmethod
    def encode(param: str) -> str:
        """Return a hashed string using the static salt from config."""
        current_app.logger.debug(f'encoding for string {param}')
        api_key = current_app.config.get('PAYBC_API_KEY')
        return hashlib.md5(f'{param}{api_key}'.encode()).hexdigest()  # NOSONAR as PayBC needs MD5

    @staticmethod
    def is_valid_checksum(param: str, hash_val: str) -> bool:
        """Validate if the checksum matches."""
        api_key = current_app.config.get('PAYBC_API_KEY')
        return hashlib.md5(f'{param}{api_key}'.encode()).hexdigest() == hash_val  # NOSONAR as PayBC needs MD5

    @staticmethod
    def parse_url_params(url_params: str) -> Dict:
        """Parse URL params and return dict of parsed url params."""
        parsed_url: dict = {}
        if url_params is not None:
            if url_params.startswith('?'):
                url_params = url_params[1:]
            parsed_url = dict(parse_qsl(url_params))

        return parsed_url
