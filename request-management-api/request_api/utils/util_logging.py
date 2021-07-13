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
import sys, os, re, datetime, logging.config
from os import path
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

def setup_logging(conf):
    """Create the services logger.

    TODO should be reworked to load in the proper loggers and remove others
    """
    if conf and path.isfile(conf):
        logfilepath = 'request_api/logs/logfile.log'
        logdir = os.path.dirname(logfilepath)
        # root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # logdir = os.path.join(root, 'logs')
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        logging.config.fileConfig(conf)
        print('Configure logging, from conf:{}'.format(conf), file=sys.stdout)
    else:
        print('Unable to configure logging, attempted conf:{}'.format(conf), file=sys.stderr)

def setup_filelogging(app):

    """ 
    Log file setup 
    """
    log_level = logging.INFO    
    logfilepath = 'request_api/logs/logfile.log'
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    log_file = os.path.abspath(logfilepath)
    log_format = '%(asctime)s - %(levelname)s - %(message)s'  ##TODO: formatter has to be taken from logging.config
    log_level = 10
    handler = TimedRotatingFileHandler(log_file, when='d', interval=1, backupCount=5)
    handler.setLevel(log_level)
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # add a suffix which you want
    handler.suffix = '%Y-%m-%d_%H-%M-%S'

    #need to change the extMatch variable to match the suffix for it
    # handler.extMatch = re.compile(r'^\d{8}$') 

    # finally add handler to logger    
    app.logger.addHandler(handler)  
