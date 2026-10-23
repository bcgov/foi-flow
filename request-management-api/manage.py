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

"""Manage the database and some other items required to run the API
"""
import logging

import click
from flask.cli import FlaskGroup
from flask_migrate import Migrate
from flask_migrate.cli import db as db_commands

# models included so that migrate can build the database migrations
from request_api import models  # pylint: disable=unused-import
from request_api import create_app
from request_api.models import db

logger = logging.getLogger(__name__)

## python manage.py db migrate
## python manage.py db upgrade


APP = create_app()
MIGRATE = Migrate(APP, db)
MANAGER = FlaskGroup(create_app=lambda: APP)

MANAGER.add_command(db_commands, 'db')


@MANAGER.command('list_routes')
def list_routes():
    output = []
    for rule in APP.url_map.iter_rules():

        methods = ','.join(rule.methods)
        line = ("{:50s} {:20s} {}".format(rule.endpoint, methods, rule.rule))
        output.append(line)

    for line in sorted(output):
        click.echo(line)


if __name__ == '__main__':
    logging.log(logging.INFO, 'Running the Manager')
    MANAGER()
