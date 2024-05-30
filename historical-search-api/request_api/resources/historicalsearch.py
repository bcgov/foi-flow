from flask import g, request, jsonify
import flask
from flask_restx import Namespace, Resource
from flask_cors import cross_origin

from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins, getrequiredmemberships
from request_api.auth import AuthHelper, auth
from request_api.tracer import Tracer
from request_api.exceptions import BusinessException
from request_api.services.historicalrequestservice import historicalrequestservice
import json

API = Namespace('FOIHistoricalSearch', description='Endpoints for FOI Historical search')
TRACER = Tracer.get_instance()

@cors_preflight('GET,OPTIONS')
@API.route('/advancedsearch')
class AdvancedHistoricalSearch(Resource):
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
           
            DEFAULT_SIZE = 10
            DEFAULT_SORT_ITEM = 'receiveddate'
            DEFAULT_SORT_ORDER = 'desc'

            print("User ID is {0}, of type {1}".format(AuthHelper.getuserid(),AuthHelper.getusertype()))
            print("Is restricted file manager - {0}".format(AuthHelper.isiaorestrictedfilemanager()))

            params = {
                'usertype': 'iao', #todo: need to update
                'groups': '',                
                'size': flask.request.args.get('size', DEFAULT_SIZE, type=int),
                'sortingitem': flask.request.args.get('sortingitem'),
                'sortingorder': flask.request.args.get('sortingorder'),

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

            if params['sortingitem'] is None:
                params['sortingitem'] = DEFAULT_SORT_ITEM
            if params['sortingorder'] is None:
                params['sortingorder'] = DEFAULT_SORT_ORDER
            if params['keywords'] is None:
                params['keywords'] = []

            statuscode = 200
            if (params['usertype'] == "iao" or params['usertype'] == "ministry"):                                                                                           
                requests = historicalrequestservice().advancedsearch(params)
            else:
                statuscode = 401   

            return requests, statuscode
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500