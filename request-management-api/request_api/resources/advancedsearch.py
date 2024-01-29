from flask import g, request, jsonify
import flask
from flask_restx import Namespace, Resource
from flask_cors import cross_origin

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.utils.enums import MinistryTeamWithKeycloackGroup, UserGroup
from request_api.auth import AuthHelper, auth
from request_api.tracer import Tracer
from request_api.exceptions import BusinessException
from request_api.services.dashboardservice import dashboardservice

API = Namespace('FOI Flow Dashboard', description='Endpoints for Dashboard')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/advancedsearch')
class DashboardPagination(Resource):
    """ Retrives the foi request based on the queue type.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @cors_preflight('GET,POST,OPTIONS')
    @auth.ismemberofgroups(getrequiredmemberships())
    def get():
        try:
            DEFAULT_PAGE = 1
            DEFAULT_SIZE = 10
            DEFAULT_SORT_ITEMS = ['currentState']
            DEFAULT_SORT_ORDERS = ['desc']

            params = {
                'usertype': AuthHelper.getusertype(),
                'groups': AuthHelper.getusergroups(),
                'page': flask.request.args.get('page', DEFAULT_PAGE, type=int),
                'size': flask.request.args.get('size', DEFAULT_SIZE, type=int),
                'sortingitems': flask.request.args.getlist('sortingitems[]'),
                'sortingorders': flask.request.args.getlist('sortingorders[]'),

                'requeststate': flask.request.args.getlist('requestState[]'),
                'requeststatus': flask.request.args.getlist('requestStatus[]'),
                'requesttype': flask.request.args.getlist('requestType[]'),
                'requestflags': flask.request.args.getlist('requestFlags[]'),
                'publicbody': flask.request.args.getlist('publicBodies[]'),

                'daterangetype': flask.request.args.get('dateRangeType', None, type=str),
                'fromdate': flask.request.args.get('fromDate', None, type=str),
                'todate': flask.request.args.get('toDate', None, type=str),

                'search': flask.request.args.get('search', None, type=str),
                'keywords': flask.request.args.getlist('keywords[]'),

                'userid': flask.request.args.get('userid', None, type=str)
            }

            if len(params['sortingitems']) == 0:
                params['sortingitems'] = DEFAULT_SORT_ITEMS
            if len(params['sortingorders']) == 0:
                params['sortingorders'] = DEFAULT_SORT_ORDERS
            if params['requeststate'] is None:
                params['requeststate'] = []
            if params['requeststatus'] is None:
                params['requeststatus'] = []
            if params['requesttype'] is None:
                params['requesttype'] = []
            if params['publicbody'] is None:
                params['publicbody'] = []
            if params['keywords'] is None:
                params['keywords'] = []

            statuscode = 200
            if (params['usertype'] == "iao" or params['usertype'] == "ministry"):                                                                                           
                requests = dashboardservice().advancedsearch(params)
            else:
                statuscode = 401   

            return requests, statuscode
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500