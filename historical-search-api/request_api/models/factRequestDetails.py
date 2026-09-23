from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging
from dateutil.parser import parse


class factRequestDetails(db.Model):
    __tablename__ = 'factRequestDetails' 
    # Defining the columns
    foirequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)

    @classmethod
    def getrequestbyid(cls, isiaorestictedmanager:False, requestid):        
        request = {}
        try:
            sql = """select 
            rd.visualrequestfilenumber,
            rd.primaryusername,
            rt.requesttypename,
            rm.receivedmodename,
            dm.deliverymodename,
            rqt.requestertypename,
            r.firstname, r.middlename, r.lastname, r.company, r.email, r.workphone1, r.workphone2, r.mobile, r.home,	
            r2.firstname as behalffirstname, r2.middlename as behalfmiddlename, r2.lastname as behalflastname,
            rs.requeststatusname,
            a.address1, a.address2, a.city, a.state, a.country, a.zipcode,
            rd.description, rd.startdate, rd.closeddate, rd.receiveddate, rd.targetdate AS duedate, rd.originaltargetdate AS originalduedate,
            rd.subject,
            rd.oipcno, rd.reviewtype, rd.reason, rd.status, rd.portfolioofficer,  rof.orderno, rof.inquirydate, rof.outcome, rof.inquirydate is not null as isinquiry
            --, rd.* 
            from public."ClosedRequestDetailsPost2018" rd
            left join public."dimRequestStatuses" rs on rs.requeststatusid = rd.requeststatusid
             --join public."factRequestRequesters" rr1 on rr1.requesterid = rd.requesterid and rr1.foirequestid = rd.foirequestid and rr1.activeflag = 'Y'
                
            left join public."dimRequesters" r on r.requesterid = rd.requesterid
            -- left join public."factRequestRequesters" rr2 on rr2.requesterid = rd.onbehalfofrequesterid and rr2.foirequestid = rd.foirequestid and rr2.activeflag = 'Y'
            left join public."dimRequesters" r2 on rd.onbehalfofrequesterid = r2.requesterid
                LEFT JOIN "dimRequesterTypes" rqt ON rd.applicantcategoryid = rqt.requestertypeid
            left join public."dimReceivedModes" rm on rm.receivedmodeid = rd.receivedmodeid
            left join public."dimAddress" a on a.addressid = rd.shipaddressid
            left join public."dimRequestTypes" rt on rt.requesttypeid = rd.requesttypeid
            left join public."dimDeliveryModes" dm on dm.deliverymodeid = rd.deliverymodeid
            left join public."factRequestOIPCFields" rof on rof.foirequestid = rd.foirequestid and rof.activeflag = 'Y'
            where rd.visualrequestfilenumber = :requestid and rd.activeflag = 'Y'"""

            if(isiaorestictedmanager == False):
                sql+= " AND rd.requesttypename NOT LIKE '%Restricted%'"
            
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                request["axisRequestId"] = row['visualrequestfilenumber']
                request["currentState"] = row['requeststatusname']
                request["assignedTo"] = row['primaryusername']
                request["requeststatuslabel"] = 'closed'                
                request["firstName"] = row['firstname']
                request["lastName"] = row['lastname']
                request["middleName"] = row['middlename']
                request["businessName"] = row['company']
                request["category"] = row['requestertypename']
                request['additionalPersonalInfo'] = {}
                request['additionalPersonalInfo']["anotherFirstName"] = row['behalffirstname']
                request['additionalPersonalInfo']["anotherLastName"] = row['behalflastname']
                request['additionalPersonalInfo']["anotherMiddleName"] = row['behalfmiddlename']
                request["email"] = row['email']
                request["phonePrimary"] = row['home']
                request["phoneSecondary"] = row['mobile']
                request["workPhonePrimary"] = row['workphone1']
                request["workPhoneSecondary"] = row['workphone2']
                request["address"] = row['address1']
                request["addressSecondary"] = row['address2']
                request["city"] = row['city']
                request["country"] = row['country']
                request["postal"] = row['zipcode']
                request["province"] = row['state']
                request["description"] = row['description']
                request["subjectCode"] = row['subject']
                request["receivedDateUF"] = row['receiveddate'].strftime('%Y-%m-%d')
                request["requestProcessStart"] = row['startdate'].strftime('%Y-%m-%d')
                request["originalDueDate"] = row['originalduedate'].strftime('%Y-%m-%d')
                request["dueDate"] = row['duedate'].strftime('%Y-%m-%d')
                request["closedate"] = row['closeddate'].strftime('%Y-%m-%d')
                request["requestType"] = row['requesttypename']
                request["receivedMode"] = row['receivedmodename']
                request["deliveryMode"] = row['deliverymodename']                
                request["subjectCode"] = row['subject']
                if row['requesttypename'] == 'Review':
                    request['isoipcreview'] = True
                    request['oipcdetails'] = [{}]
                    request['oipcdetails'][0]['oipcno'] = row['oipcno']
                    request['oipcdetails'][0]['receiveddate'] = row['receiveddate'].strftime('%Y-%m-%d')
                    request['oipcdetails'][0]['closeddate'] = row['closeddate'].strftime('%Y-%m-%d')
                    request['oipcdetails'][0]['reviewetype'] = row['reviewtype']
                    request['oipcdetails'][0]['reason'] = row['reason']
                    request['oipcdetails'][0]['status'] = row['status']
                    request['oipcdetails'][0]['investigator'] = row['portfolioofficer']
                    request['oipcdetails'][0]['outcome'] = row['outcome']
                    request['oipcdetails'][0]['isinquiry'] = row['isinquiry']
                    if row['isinquiry']:
                        request['oipcdetails'][0]['inquiryattributes'] = {}
                        request['oipcdetails'][0]['inquiryattributes']['inquirydate'] = row['inquirydate']
                        request['oipcdetails'][0]['inquiryattributes']['orderno'] = row['orderno']

                # requestdetails["assignedToFirstName"] = row["assignedtofirstname"]
                # requestdetails["assignedToLastName"] = row["assignedtolastname"]
                # requestdetails["bcgovcode"] = row["bcgovcode"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return request
    
    @classmethod
    def getdescriptionhistorybyid(cls, requestid):
        history = []
        try:
            sql = """
                with dbrequestid as (select foirequestid from public."ClosedRequestDetailsPost2018" where visualrequestfilenumber = :requestid)
                SELECT 
                description,
                modifieddate,
                createddate,
                modifiedbyusername
                FROM public."factRequestDetails"
				where foirequestid = (select foirequestid from dbrequestid)
                and runcycleid in (select max(runcycleid) from public."factRequestDetails"                
                    where foirequestid = (select foirequestid from dbrequestid)
                    group by description)	
                ORDER BY runcycleid DESC"""
            rs = db.session.execute(text(sql), {'requestid': requestid})
            for row in rs:
                entry = {}
                entry["createdAt"] = row['modifieddate'].strftime('%Y-%m-%d')
                entry["createdBy"] = row['modifiedbyusername']
                entry["description"] = row['description']
                history.append(entry)
                # requestdetails["assignedToFirstName"] = row["assignedtofirstname"]
                # requestdetails["assignedToLastName"] = row["assignedtolastname"]
                # requestdetails["bcgovcode"] = row["bcgovcode"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return history

    @classmethod
    def getadvancedsearchresults(cls,isiaorestictedmanager:False, params):
        searchresults = []
        count = 0
        try:
            basequery = 'SELECT count(*) OVER() AS full_count\
                            ,foirequestid \
                            ,requesttypename \
                            ,applicantname \
                            ,visualrequestfilenumber \
                            ,oipcno \
                            ,subject \
                            ,primaryusername as assignee \
                            ,receiveddate \
                            ,description \
                            ,requeststatus \
                            ,closeddate \
                            ,ministry \
                            ,officeid \
                            FROM \
                            public."ClosedRequestDetailsPost2018"'

            conditions = []
            queryparams = {}

            search_type = params.get('search')

            if search_type == 'requestdescription':
                search_column = 'description'
            elif search_type == 'applicantname':
                search_column = 'applicantname'
            elif search_type == 'assigneename':
                search_column = 'primaryusername'
            elif search_type in ('idnumber', 'axisrequest_number'):
                search_column = 'visualrequestfilenumber'
            elif search_type == 'oipc_number':
                search_column = 'oipcno'
            else:
                search_column = None

            if search_column is not None:
                for idx, keyword in enumerate(params.get('keywords') or []):
                    parameter_name = f'search_{idx}'
                    conditions.append(
                        f'LOWER({search_column}) LIKE LOWER(:{parameter_name})'
                    )
                    queryparams[parameter_name] = f'%{keyword}%'

            elif search_type == 'businessName':
                for idx, keyword in enumerate(params.get('keywords') or []):
                    parameter_name = f'businessname_{idx}'

                    conditions.append(
                        f'EXISTS (SELECT 1 FROM public."dimRequesters" r '
                        f'WHERE r.requesterid = public."ClosedRequestDetailsPost2018".requesterid '
                        f'AND LOWER(r.company) LIKE LOWER(:{parameter_name}))'
                    )

                    queryparams[parameter_name] = f'%{keyword.strip()}%'

            requesttypeconditions = []

            for idx, requesttype in enumerate(
                (params.get('requesttype') or []) +
                (params.get('requestflags') or [])
            ):
                if requesttype == 'oipc':
                    requesttype = 'review'

                parameter_name = f'requesttype_{idx}'

                requesttypeconditions.append(
                    f'LOWER(requesttypename) LIKE LOWER(:{parameter_name})'
                )
                queryparams[parameter_name] = f'%{requesttype}%'

            if requesttypeconditions:
                conditions.append(
                    '(' + ' OR '.join(requesttypeconditions) + ')'
                )

            datefilter = params.get('daterangetype')

            if datefilter == 'receivedDate':
                date_column = 'receiveddate'
            elif datefilter == 'duedate':
                date_column = 'targetdate'
            elif datefilter == 'closedate':
                date_column = 'closeddate'
            elif datefilter:
                raise ValueError(
                    'Unsupported historical search date range type'
                )
            else:
                date_column = None

            if date_column is not None:
                if params.get('fromdate'):
                    conditions.append(
                        f'{date_column} >= :fromdate'
                    )
                    queryparams['fromdate'] = params.get('fromdate')

                if params.get('todate'):
                    conditions.append(
                        f'{date_column} <= :todate'
                    )
                    queryparams['todate'] = params.get('todate')

            if not conditions:
                return {'results': [], 'count': 0}

            if isiaorestictedmanager == False:
                conditions.append(
                    "requesttypename NOT LIKE '%Restricted%'"
                )

            basequery += ' WHERE ' + ' AND '.join(conditions)

            sortingitem = params.get('sortingitem')

            if sortingitem == 'applicantname':
                sort_column = 'applicantname'
            elif sortingitem == 'requesttype':
                sort_column = 'requesttype'
            elif sortingitem == 'axisrequestid':
                sort_column = 'visualrequestfilenumber'
            elif sortingitem == 'oipcno':
                sort_column = 'oipcno'
            elif sortingitem == 'assignee':
                sort_column = 'assignee'
            elif sortingitem == 'receiveddate':
                sort_column = 'receiveddate'
            else:
                raise ValueError(
                    'Unsupported historical search sort field'
                )

            sortingorder = str(
                params.get('sortingorder', '')
            ).lower()

            if sortingorder == 'asc':
                sort_order = 'ASC'
            elif sortingorder == 'desc':
                sort_order = 'DESC'
            else:
                raise ValueError(
                    'Unsupported historical search sort order'
                )

            basequery += f' ORDER BY {sort_column} {sort_order}'

            if params.get('size') is not None:
                size = int(params['size'])
                page = int(params.get('page', 1))

                if size < 1 or page < 1:
                    raise ValueError(
                        'Historical search page and size must be positive integers'
                    )

                queryparams['limit_value'] = size
                queryparams['offset_value'] = (page - 1) * size

                basequery += (
                    ' LIMIT :limit_value OFFSET :offset_value'
                )
            else:
                basequery += ' LIMIT 100'

            rs = db.session.execute(
                text(basequery),
                queryparams
            )

            for row in rs:
                searchresults.append({
                    "axisrequestid": row["visualrequestfilenumber"],
                    "description": row["description"],
                    "assignee": row["assignee"],
                    "requeststatus": row["requeststatus"],
                    "applicantname": row["applicantname"],
                    "requesttype": row["requesttypename"],
                    "receiveddate": row["receiveddate"],
                    "oipcno": row["oipcno"]
                })
                count = row["full_count"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return {'results': searchresults, 'count': count}
              