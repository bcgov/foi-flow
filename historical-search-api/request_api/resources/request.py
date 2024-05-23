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
from flask_restx import Namespace, Resource
from flask_expects_json import expects_json
from flask_cors import cross_origin
from request_api.auth import auth, AuthHelper
from request_api.tracer import Tracer
from request_api.utils.util import  cors_preflight, allowedorigins,str_to_bool,canrestictdata
from request_api.exceptions import BusinessException
# from request_api.services.rawrequestservice import rawrequestservice
# from request_api.services.documentservice import documentservice
# from request_api.services.eventservice import eventservice
# from request_api.services.unopenedreportservice import unopenedreportservice
from request_api.services.historicalrequestservice import historicalrequestservice
# from request_api.utils.enums import StateName
import json
import asyncio
from jose import jwt as josejwt
import holidays
from datetime import datetime, timedelta
import os
import pytz



API = Namespace('FOIRawRequests', description='Endpoints for FOI request management')
TRACER = Tracer.get_instance()
with open('request_api/schemas/schemas/rawrequest.json') as f:
        schema = json.load(f)

INVALID_REQUEST_ID = 'Invalid Request Id'

SHORT_DATE_FORMAT = '%Y-%m-%d'
LONG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

@cors_preflight('GET,POST,OPTIONS')
@API.route('/foihistoricalrequest/<requestid>')
class FOIRawRequest(Resource):
    """Retrieve historical request details from EDW"""

    @staticmethod
    @TRACER.trace()
    @cross_origin(origins=allowedorigins())       
    # @auth.require
    def get(requestid):
        try : 
            jsondata = {}
            statuscode = 200
            # requestidisinteger = int(requestid)
            # if requestidisinteger :                
            #     baserequestinfo = rawrequestservice().getrawrequest(requestid)

            #     assignee = baserequestinfo['assignedTo']
            #     isiaorestricted = baserequestinfo['isiaorestricted']
            #     # print('Request # {0} Assigned to {1} and is restricted {2} '.format(requestid,assignee,isiaorestricted))
            #     if(isiaorestricted and canrestictdata(requestid,assignee,isiaorestricted,True)):
            #         jsondata = {'status': 401, 'message':'Restricted Request'}
            #         statuscode = 401
            #     else:
            #         jsondata = json.dumps(baserequestinfo)
            #         statuscode = 200

#             select 
# 	rt.requesttypename,
# 	rm.receivedmodename,
# 	dm.deliverymodename,
# 	rqt.requestertypename,
# 	r.firstname, r.lastname, r.company, r.email, r.workphone1, r.workphone2, r.mobile, r.home,	
# 	r2.firstname, r2.lastname,
# 	rs.requeststatusname,
# 	a.address1, a.address2, a.city, a.state, a.country, a.zipcode,
# 	rd.description, rd.startdate, rd.closeddate, rd.receiveddate, rd.targetdate AS duedate,
# 	rd.subject
# 	--, rd.* 
# 	from public."factRequestDetails" rd
# join public."dimRequestStatuses" rs on rs.requeststatusid = rd.requeststatusid
# join public."factRequestRequesters" rr1 on rr1.requesterid = rd.requesterid and rr1.foirequestid = rd.foirequestid and rr1.activeflag = 'Y'
	
# join public."dimRequesters" r on rr1.requesterid = r.requesterid
# left join public."factRequestRequesters" rr2 on rr2.requesterid = rd.onbehalfofrequesterid and rr2.foirequestid = rd.foirequestid and rr2.activeflag = 'Y'
# left join public."dimRequesters" r2 on rr2.requesterid = r2.requesterid
# 	LEFT JOIN "dimRequesterTypes" rqt ON rd.applicantcategoryid = rqt.requestertypeid
# join public."dimReceivedModes" rm on rm.receivedmodeid = rd.receivedmodeid
# join public."dimAddress" a on a.addressid = rd.shipaddressid
# join public."dimRequestTypes" rt on rt.requesttypeid = rd.requesttypeid
# join public."dimDeliveryModes" dm on dm.deliverymodeid = rd.deliverymodeid
# where rd.visualrequestfilenumber = 'CFD-2023-30109' and rd.activeflag = 'Y'


            return jsondata , statuscode 
        except ValueError:
            return {'status': 500, 'message':INVALID_REQUEST_ID}, 500    
        except BusinessException as exception:            
            return {'status': exception.status_code, 'message':exception.message}, 500

    