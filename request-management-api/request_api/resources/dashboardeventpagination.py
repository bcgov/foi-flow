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
from request_api.services.dashboardeventservice import dashboardeventservice

API = Namespace('FOIEvent', description='Endpoints for FOI event management')
TRACER = Tracer.get_instance()
"""Custom exception messages
"""
EXCEPTION_MESSAGE_BAD_REQUEST='Bad Request'
        
     
@cors_preflight('GET,OPTIONS')
@API.route('/eventpagination')
@API.route('/eventpagination/<queuetype>')
class EventPagination(Resource):
    """ Retrives the foi request based on the queue type.
    """
    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())
    @auth.require
    @cors_preflight('GET,OPTIONS')
    def get(queuetype = "all"):
        try:
            DEFAULT_PAGE = 1
            DEFAULT_SIZE = 10
            DEFAULT_SORT_ITEMS = ['createdat']
            DEFAULT_SORT_ORDERS = ['desc']
            DEFAULT_FILTER_FIELDS = [
                                        'axisRequestId',
                                        'createdby',
                                        'to',
                                        'notification',
                                        'assignedToFirstName',
                                        'assignedToLastName',
                                        'assignedministrypersonFirstName',
                                        'assignedministrypersonLastName',
                                        'createdat'
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

            events = []
            statuscode = 200
            if AuthHelper.getusertype() == "iao" or AuthHelper.getusertype() == "ministry":  
                groups =  AuthHelper.getusergroups() if AuthHelper.getusertype() == "iao" else AuthHelper.getministrygroups()      
                                                                                              
                events = dashboardeventservice().geteventqueuepagination(queuetype, groups, _page, _size, _sortingitems, _sortingorders, _filterfields, _keyword, _additionalfilter, _userid)
            else:
                statuscode = 401  

            return events, statuscode
        except BusinessException as exception:
            return {'status': exception.status_code, 'message':exception.message}, 500



