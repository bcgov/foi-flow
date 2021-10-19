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
"""Bring in the common JWT Manager."""
from functools import wraps
from http import HTTPStatus

from flask import g, request
from flask_jwt_oidc import JwtManager
from jose import jwt as josejwt

jwt = (
    JwtManager()
)  # pylint: disable=invalid-name; lower case name as used by convention in most Flask apps


class Auth:
    """Extending JwtManager to include additional functionalities."""

    @classmethod
    def require(cls, f):
        """Validate the Bearer Token."""

        @jwt.requires_auth
        @wraps(f)
        def decorated(*args, **kwargs):
            g.authorization_header = request.headers.get("Authorization", None)
            g.token_info = g.jwt_oidc_token_info
            return f(*args, **kwargs)

        return decorated
    
    @classmethod
    def ismemberofgroups(cls, groups):
        """Check that at least one of the realm groups are in the token.
        Args:
            groups [str,]: Comma separated list of valid roles
        """

        def decorated(f):
            # Token verification is commented here with an expectation to use this decorator in conjuction with require.
            #@Auth.require
            @wraps(f)
            def wrapper(*args, **kwargs):
                _groups = groups.split(',')
                token = jwt.get_token_auth_header()
                unverified_claims = josejwt.get_unverified_claims(token)
                userGroups = unverified_claims['groups']
                userGroups = [userGroup.replace('/','',1) if userGroup.startswith('/') else userGroup for userGroup in userGroups]
                exists = False
                for group in _groups:
                    if group in userGroups: 
                       exists = True
                retval = "Unauthorized" , 401
                if exists == True:            
                    return f(*args, **kwargs)
                return retval

            return wrapper

        return decorated
    
auth = (
    Auth()
)


class AuthHelper:
    
    def getUserId():
        token = request.headers.get("Authorization", None)
        unverified_claims = josejwt.get_unverified_claims(token.partition("Bearer")[2].strip())
        return unverified_claims['preferred_username']
    
    def isMinistryMember():
        token = request.headers.get("Authorization", None)
        unverified_claims = josejwt.get_unverified_claims(token.partition("Bearer")[2].strip())
        userGroups = unverified_claims['groups']
        userGroups = [userGroup.replace('/','',1) if userGroup.startswith('/') else userGroup for userGroup in userGroups]
        for group in userGroups:
            if group.endswith("Ministry Team"):
                return True
        return False
            
    def getUserGroups():
        token = request.headers.get("Authorization", None)
        unverified_claims = josejwt.get_unverified_claims(token.partition("Bearer")[2].strip())
        userGroups = unverified_claims['groups']
        userGroups = [userGroup.replace('/','',1) if userGroup.startswith('/') else userGroup for userGroup in userGroups]
        return userGroups