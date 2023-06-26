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
"""Centralized setup of logging for the service."""
import os, logging, logging.config

LOG_ROOT = os.getenv('LOG_ROOT', "DEBUG").upper()
LOG_BASIC = os.getenv('LOG_BASIC', "WARNING").upper()
LOG_TRACING = os.getenv('LOG_TRACING', "ERROR").upper()
LOGGING_FORMAT = '[%(asctime)s] %(levelname)-8s (%(name)s) <%(module)s.py:%(filename)s:%(lineno)d>.%(funcName)s: %(message)s'

def configure_logging():    
    # Set up basic logging for the application.
    logging.basicConfig(format=LOGGING_FORMAT, level=string_to_debug_level(LOG_ROOT))
    temp_logger = logging.getLogger()
    print("==> Root logger of '" + temp_logger.name + "' set to level: " + LOG_ROOT)
    
    #   Set up defaults.   
    for name in logging.root.manager.loggerDict:        
        module_logger = logging.getLogger(name)
        module_prefix = name.split('.')[0] if name not in (None,'') else "NOTSET"
        module_logger_level = os.getenv(make_env_name(module_prefix), LOG_BASIC).upper()
        print("--> Logger " + name + " set to level LOG_BASIC level of " + module_logger_level)
        module_logger.setLevel(string_to_debug_level(module_logger_level))
    
    # Tracing Log Config    
    logging.getLogger("jaeger_tracing").setLevel(string_to_debug_level(LOG_TRACING))

def make_env_name(name):
    return ("LOG_" + name.upper())

def string_to_debug_level(debug_string):
    level = debug_string.upper()
    if level in ('CRITICAL', 'ERROR', 'WARNING', 'INFO','DEBUG'):
        result = logging.getLevelName(level)
    else:
        result = logging.WARNING
    return result

