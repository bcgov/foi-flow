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
            rd.subject
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
        try:
            basequery = 'SELECT foirequestid \
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
                            public."ClosedRequestDetailsPost2018" WHERE '

            filterbysearchcondition =[]        

            if(params['search'] == 'requestdescription'):
                for keyword in params['keywords']:
                    filterbysearchcondition.append("LOWER(description) like LOWER('%{0}%')".format(keyword))
            elif(params['search'] == 'applicantname'):
                for keyword in params['keywords']:
                    filterbysearchcondition.append("LOWER(applicantname) like LOWER('%{0}%')".format(keyword))
            elif(params['search'] == 'assigneename'):
                for keyword in params['keywords']:
                    filterbysearchcondition.append("LOWER(primaryusername) like LOWER('%{0}%')".format(keyword))
            elif(params['search'] == 'idnumber' or params['search'] == 'axisrequest_number'):
                for keyword in params['keywords']:
                    filterbysearchcondition.append("LOWER(visualrequestfilenumber) like LOWER('%{0}%')".format(keyword))

            conditioncount = len(filterbysearchcondition) 

            for idx,searchcondition in enumerate(filterbysearchcondition):                                
                basequery+= ' {0} '.format(searchcondition)
                
                if(idx!=(conditioncount-1)):
                    basequery+= ' AND '

            if(conditioncount == 0):
                basequery+= "LOWER(description) like LOWER('%{0}%')".format(keyword)

            if(isiaorestictedmanager == False):
                basequery+= " AND requesttypename NOT LIKE '%Restricted%'"

            basequery+= ' ORDER BY {0} {1}'.format(params['sortingitem'],params['sortingorder'])

            if params['size'] is not None:
                basequery+= ' LIMIT {0}'.format(params['size'])
            else:
                basequery+= ' LIMIT 100'
        
            rs = db.session.execute(text(basequery))
            
            for row in rs:            
                searchresults.append({"axisrequestid": row["visualrequestfilenumber"], "description": row["description"], "assignee": row["assignee"], "requeststatus": row["requeststatus"], "applicantname": row["applicantname"], "requesttype": row["requesttypename"],"receiveddate": row["receiveddate"],"oipcno": row["oipcno"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return searchresults
              