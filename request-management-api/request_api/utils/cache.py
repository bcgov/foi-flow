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
import os

import request_api

class Config(object):
    ## type 'redis' is deprecated
    CACHE_TYPE ='RedisCache'
    
    CACHE_REDIS_HOST = os.getenv('FOI_REQUESTQUEUE_REDISHOST')
    CACHE_REDIS_PORT = os.getenv('FOI_REQUESTQUEUE_REDISPORT')
    CACHE_REDIS_DB = 0
    CACHE_REDIS_URL = os.getenv('FOI_REQUESTQUEUE_REDISURL')
    CACHE_DEFAULT_TIMEOUT = os.getenv('CACHE_TIMEOUT')
    CACHE_KEY_PPREFIX = 'foi'
        
    ## include code of function in hash
    CACHE_SOURCE_CHECK = True

## If true, bypass cache
def cache_filter(*args, **kwargs):
    if os.getenv('CACHE_ENABLED') != 'Y':
        return True
    return False

## If True, cache response  
def response_filter(resp):
    if resp[-1] == 200 and resp[0] not in (None, '', '[]'):
        return True
    else:
        return False

