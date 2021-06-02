# Copyright © 2019 Province of British Columbia
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
import logging.config
import sys
from os import path
import os
from pathlib import Path

def setup_logging(conf):
    """Create the services logger.

    TODO should be reworked to load in the proper loggers and remove others
    """
    if conf and path.isfile(conf):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # root = Path(__file__).parent
        logdir = os.path.join(root, 'logs')
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        logging.config.fileConfig(conf)
        print('Configure logging, from conf:{}'.format(conf), file=sys.stdout)
    else:
        print('Unable to configure logging, attempted conf:{}'.format(conf), file=sys.stderr)

def setup_filelogging(app):
    log_level = logging.INFO
 
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    logdir = os.path.join(root, 'logs')
    if not os.path.exists(logdir):
        os.mkdir(logdir)
    log_file = os.path.join(logdir, 'app.log')
    handler = logging.FileHandler(log_file)
    handler.setLevel(log_level)
    app.logger.addHandler(handler) 
    app.logger.setLevel(log_level)