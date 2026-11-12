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


from flask import g, request, Response
from flask_restx import Namespace, Resource, cors
from flask_expects_json import expects_json
from request_api.auth import auth
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins
from request_api.exceptions import BusinessException, Error
from request_api.services.workflowservice import workflowservice
from request_api.services.workflowoutboxservice import workflowoutboxservice, AckResult, EventKind
from request_api.services import paymentslabackfillapi as backfillapi
from request_api.services.paymentslabackfillservice import report_csv_text
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


@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/events/<eventid>/claim')
class FOIWorkflowEventClaim(Resource):
    """n8n asks whether it may process an event. Answers proceed, duplicate, in_progress or stale."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isworkflowserviceaccount()
    def post(eventid):
        eventid = _validuuid(eventid)
        body = request.get_json(silent=True) or {}
        executionid = body.get('executionid')
        also = body.get('also_advance') or []
        if eventid is None or executionid in (None, '') or not isinstance(also, list) \
                or not all(isinstance(item, dict) for item in also):
            return {'status': False, 'message': 'A valid event id and executionid are required'}, 400
        try:
            decision = workflowoutboxservice().claim(
                eventid, str(executionid), kind=body.get('kind') or EventKind.action,
                scope=body.get('scope'), scopekey=body.get('scopekey'), occurredat=body.get('occurred_at'),
                requestids=body.get('requestids') if isinstance(body.get('requestids'), dict) else {})
            logging.info("workflow event claim event_id=%s execution=%s decision=%s", eventid, executionid, decision)
            return {'status': True, 'decision': decision}, 200
        except ValueError as err:
            return {'status': False, 'message': str(err)}, 400


@cors_preflight('GET,OPTIONS')
@API.route('/foiworkflow/executions/<executionid>/event')
class FOIWorkflowExecutionEvent(Resource):
    """The event an n8n execution claimed (found: false when it failed before claiming). No payload."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isworkflowserviceaccount()
    def get(executionid):
        found = workflowoutboxservice().findbyexecution(executionid)
        if found is None:
            return {'status': True, 'found': False}, 200
        return dict(found, status=True, found=True), 200


@cors_preflight('GET,OPTIONS')
@API.route('/foiworkflow/events')
class FOIWorkflowEvents(Resource):
    """Lists outbox events; DEAD and FAILED (including NO_OUTCOME) by default. Payloads are not returned. FOI admins only."""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isfoiadmin()
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
    @auth.isfoiadmin()
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
    @auth.isfoiadmin()
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


def _backfillresponse(payload, status):
    # the report holds Form.io ids, which make up the payment links
    return _nostore(Response(json.dumps(payload), status=status, mimetype='application/json'))


def _nostore(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


def _runpaymentslabackfill(apply):
    """One-time Camunda to n8n payment SLA backfill. Only while PAYMENT_SLA_BACKFILL_ENABLED=true."""
    if not backfillapi.enabled():
        return _backfillresponse({'status': False, 'message': 'The payment SLA backfill is not enabled'}, 404)
    options, error = backfillapi.parse_options(request.get_json(silent=True), apply)
    if error:
        return _backfillresponse({'status': False, 'message': error}, 400)
    operator, mode = str(AuthHelper.getuserid()), 'APPLY' if apply else 'dry run'
    logging.info("payment SLA backfill %s requested by %s: include_expired=%s ministry_request_ids=%s",
                 mode, operator, options['include_expired'], options['ministry_request_ids'])
    status, payload, report = backfillapi.execute(options, apply, operator)
    logging.info("payment SLA backfill %s by %s finished with HTTP %s plan_hash=%s",
                 mode, operator, status, (report or {}).get('run', {}).get('plan_hash'))
    if status == 200 and request.args.get('format', 'json').lower() == 'csv':
        response = Response(report_csv_text(report).encode('utf-8'), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=payment_sla_backfill_%s_%s.csv' % (
            report['run']['mode'], report['run']['id'])
        response.headers['X-Plan-Hash'] = report['run']['plan_hash']
        return _nostore(response)
    return _backfillresponse(payload, status)


@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/payment-sla-backfill/dry-run')
class FOIPaymentSlaBackfillDryRun(Resource):
    """Reports what the backfill would write and returns its plan hash. Writes nothing.

    Body: {"include_expired": false, "ministry_request_ids": []}. ?format=csv downloads the per-record results for
    review in Excel; the plan hash is then in the X-Plan-Hash header.
    """

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isfoiadmin()
    def post():
        return _runpaymentslabackfill(apply=False)


@cors_preflight('POST,OPTIONS')
@API.route('/foiworkflow/payment-sla-backfill/apply')
class FOIPaymentSlaBackfillApply(Resource):
    """Writes the rows of a reviewed dry run. Body: the dry-run body plus its "plan_hash".

    Answers 409 and writes nothing when the plan changed since that dry run.
    """

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @auth.isfoiadmin()
    def post():
        return _runpaymentslabackfill(apply=True)
