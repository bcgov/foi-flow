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
@API.route('/dashboardpagination', defaults={'queuetype':None})
@API.route('/dashboardpagination/<queuetype>')
class DashboardPagination(Resource):
    """ Retrives the foi request based on the queue type.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @cors_preflight('GET,POST,OPTIONS')
    @auth.ismemberofgroups(getrequiredmemberships())
    def get(queuetype = "all"):
        try:
            DEFAULT_PAGE = 1
            DEFAULT_SIZE = 10
            DEFAULT_SORT_ITEMS = ['currentState']
            DEFAULT_SORT_ORDERS = ['desc']
            DEFAULT_FILTER_FIELDS = [
                                        'idNumber',
                                        'axisRequestId',
                                        'currentState',
                                        'firstName',
                                        'lastName',
                                        'assignedToFirstName',
                                        'assignedToLastName',
                                        'assignedministrypersonFirstName',
                                        'assignedministrypersonLastName',
                                        'requestType'
                                    ]
            DEFAULT_ADDITIONAL_FILTER = 'All'
            _page = flask.request.args.get('page', DEFAULT_PAGE, type=int)
            _size = flask.request.args.get('size', DEFAULT_SIZE, type=int)
            _sortingitems = flask.request.args.getlist('sortingitems[]')
            _sortingorders = flask.request.args.getlist('sortingorders[]')
            _filterfields = flask.request.args.getlist('filters[]')
            _additionalfilter = flask.request.args.get('additionalfilter', DEFAULT_ADDITIONAL_FILTER, type=str)
            _userid = flask.request.args.get('userid', None, type=str)
            if(len(_sortingitems) == 0):
                _sortingitems = DEFAULT_SORT_ITEMS
            if(len(_sortingorders) == 0):
                _sortingorders = DEFAULT_SORT_ORDERS
            if(len(_filterfields) == 0):
                _filterfields = DEFAULT_FILTER_FIELDS
            _keyword = flask.request.args.get('keyword', None, type=str)

            groups = AuthHelper.getusergroups()
            print("authhelper: ",AuthHelper)
            print("authhelper get user type: ",AuthHelper.getusertype())
            print("groups : ",groups)
            print("queuetype : ",queuetype)
            requests = None
            statuscode = 200
            if (AuthHelper.getusertype() == "iao") and (queuetype is None or queuetype == "all"):     
                print("dashboard api")                                                                                      
                requests = dashboardservice().getrequestqueuepagination(groups, _page, _size, _sortingitems, _sortingorders, _filterfields, _keyword, _additionalfilter, _userid)
            elif  queuetype is not None and queuetype == "ministry" and AuthHelper.getusertype() == "ministry":
                print("ministry api")    
                requests = dashboardservice().getministryrequestqueuepagination(AuthHelper.getministrygroups(), _page, _size, _sortingitems, _sortingorders, _filterfields, _keyword, _additionalfilter, _userid)
            # elif (AuthHelper.getusertype() == "iao") and (queuetype is not None and queuetype == "oi"):
            #     print("OI TEAM API")
            #     requests = dashboardservice().getoirequestqueuepagination(groups, _page, _size, _sortingitems, _sortingorders, _filterfields, _keyword, _additionalfilter, _userid)
            else:
                statuscode = 401   
            print("requests : ",requests)
            
            return requests, statuscode
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500