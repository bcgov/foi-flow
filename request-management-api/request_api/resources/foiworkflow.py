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
"""API endpoints for managing a FOI Requests resource."""


from flask import g, request
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.workflowservice import workflowservice
from request_api.services.workflowoutboxservice import workflowoutboxservice, AckResult
from request_api.models.FOIWorkflowEventOutbox import OutboxStatus
import json
import uuid
from flask_cors import cross_origin
import logging

API = Namespace('FOIWorkflow', description='Endpoints for FOI workflow management')
TRACER = Tracer.get_instance()
CUSTOM_KEYERROR_MESSAGE = "Key error has occured: "

@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/<requesttype>/<requestid>/sync')
class FOIWorkflow(Resource):
    """Retrieve watchers for unopened request"""

       
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(requesttype, requestid):      
        try:
            logging.info("request details = %s | %s", requesttype, requestid)
            response = workflowservice().syncwfinstance(requesttype, requestid, True)
            return json.dumps({"message": str(response)}), 200
        except ValueError as err:
            return {'status': 500, 'message': str(err)}, 500
        except KeyError as error:
            return {'status': False, 'message': CUSTOM_KEYERROR_MESSAGE + str(error)}, 400        
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500


def _validuuid(value):
    try:
        return str(uuid.UUID(str(value)))
    except ValueError:
        return None


def _outboxresponse(result, row, notfound="Event not found", conflict="Event is not in a state that allows this change"):
    if result == AckResult.notfound:
        return {'status': False, 'message': notfound}, 404
    if result == AckResult.conflict:
        return {'status': False, 'message': conflict, 'event': workflowoutboxservice.todict(row)}, 409
    return {'status': True, 'result': result, 'event': workflowoutboxservice.todict(row)}, 200


@cors_preflight('PUT,OPTIONS')
@API.route('/foiworkflow/events/<eventid>')
class FOIWorkflowEventOutcome(Resource):
    """n8n reports the outcome of an event. Only updates the outbox row; never changes request state."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isworkflowserviceaccount()
    def put(eventid):
        eventid = _validuuid(eventid)
        body = request.get_json(silent=True) or {}
        status = body.get('status')
        if eventid is None or status not in (OutboxStatus.completed.value, OutboxStatus.failed.value):
            return {'status': False, 'message': 'A valid event id and status (COMPLETED or FAILED) are required'}, 400
        try:
            result, row = workflowoutboxservice().acknowledge(
                eventid, status, error=body.get('error'), executionid=str(body['executionid']) if body.get('executionid') else None)
            return _outboxresponse(result, row, conflict="Event cannot move from %s to %s" % (row.status if row else None, status))
        except BusinessException as exception:
            return {'status': exception.status_code, 'message': exception.message}, 500


@cors_preflight('GET,OPTIONS')
@API.route('/foiworkflow/events')
class FOIWorkflowEvents(Resource):
    """Lists outbox events; DEAD and FAILED (including NO_OUTCOME) by default. Payloads are not returned."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def get():
        valid = [status.value for status in OutboxStatus]
        statuses = [item.strip().upper() for item in request.args.get('status', 'DEAD,FAILED').split(',') if item.strip()]
        if not statuses or any(status not in valid for status in statuses):
            return {'status': False, 'message': 'status must be a comma separated list of: ' + ', '.join(valid)}, 400
        try:
            limit = min(int(request.args.get('limit', 100)), 500)
            offset = max(int(request.args.get('offset', 0)), 0)
        except ValueError:
            return {'status': False, 'message': 'limit and offset must be integers'}, 400
        return {'status': True, 'events': workflowoutboxservice().listevents(statuses, limit, offset)}, 200


@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/events/<eventid>/replay')
class FOIWorkflowEventReplay(Resource):
    """Queues one DEAD or FAILED event again, with the same event_id."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post(eventid):
        eventid = _validuuid(eventid)
        if eventid is None:
            return {'status': False, 'message': 'A valid event id is required'}, 400
        logging.info("workflow event replay requested by %s for event_id=%s", AuthHelper.getuserid(), eventid)
        result, row = workflowoutboxservice().replay(eventid)
        return _outboxresponse(result, row, conflict="Only DEAD or FAILED events can be replayed")


@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/events/replay')
class FOIWorkflowEventsReplay(Resource):
    """Queues several DEAD or FAILED events again. Body: {"eventids": [...]}."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    def post():
        eventids = (request.get_json(silent=True) or {}).get('eventids')
        if not isinstance(eventids, list) or not eventids or len(eventids) > 500 or any(_validuuid(item) is None for item in eventids):
            return {'status': False, 'message': 'eventids must be a list of 1 to 500 valid event ids'}, 400
        logging.info("workflow event bulk replay requested by %s for %s events", AuthHelper.getuserid(), len(eventids))
        results = {}
        for eventid in eventids:
            result, _ = workflowoutboxservice().replay(_validuuid(eventid))
            results[eventid] = result
        return {'status': True, 'results': results}, 200
