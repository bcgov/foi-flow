
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.RequestorType import RequestorType
from request_api.services.requestservice import requestservicegetter, requestservicecreate
from request_api.services.rawrequestservice import rawrequestservice
from request_api.auth import AuthHelper
from dateutil import tz, parser
from flask import jsonify
from datetime import datetime as datetime2
from request_api.utils.commons.datetimehandler import datetimehandler
from request_api.models.default_method_result import DefaultMethodResult
import re
import maya

class applicantservice:
    """ FOI Event Dashboard
    """

    def get_applicant_profile_by_id(self, applicantid):
        latestprofile = FOIRequestApplicant.getlatestprofilebyapplicantid(applicantid)
        applicant = FOIRequestApplicant.get_composite_applicant_profile_by_id(latestprofile['foirequestapplicantid'])
        # If composite applicant isn't found, fall back to getting applicant from FOIRequestApplicant table
        if not applicant:
            applicant = FOIRequestApplicant.get_applicant_profile_by_id(applicantid)
        applicant = self.__prepareapplicant(applicant)
        applicant['requestHistory'] = self.getapplicantrequests(applicantid)
        return applicant

    def searchapplicant(self, keywords):
        applicantqueue = []
        applicants = FOIRequestApplicant.search_composite_applicant(keywords)
        excluded_profile_ids = []
        if applicants is not None:
            for applicant in applicants:
                applicantqueue.append(self.__prepareapplicant(applicant))
                excluded_profile_ids.append(self.__first_not_null(applicant["applicantprofileid"]))
        applicantprofiles = FOIRequestApplicant.search_applicant_profiles(keywords, excluded_profile_ids)
        if applicantprofiles:
            for applicant in applicantprofiles:
                applicantqueue.append(self.__prepareapplicant(applicant))
        return applicantqueue

    def createnewapplicant(self, applicantschema, applicantpayload, userid):
        requesttype = applicantpayload.get('requesttype')
        if applicantpayload.get('foirequestid', None) and requesttype == 'foirequest':
            requests = FOIMinistryRequest.getopenrequestsbyrequestId([applicantpayload['foirequestid']])
            for request in requests:
                requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
                # requestschema.update(applicantschema)
                self.__update_applicant_data_on_request(requestschema, applicantschema, applicantpayload, "create")
                requestschema.requestApplicants = self.__prepareapplicants(requestschema, userid)
                print('\n*********\n*********\nRUQUEST SCHEMA: ', requestschema)
                responseschema = requestservicecreate().saverequestversion(
                    requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
                )
                if not responseschema.success:
                    return responseschema

        if requesttype == 'rawrequest':
            if not applicantschema.get("foiRequestApplicantID"):
                applicant = FOIRequestApplicant.from_applicant_data(applicantschema, is_new=True)
                save_result = FOIRequestApplicant.save_instance(applicant, userid)

                applicantschema['foiRequestApplicantID'] = save_result.identifier

        if applicantpayload.get('rawrequestid', None) and requesttype == 'rawrequest':
            rawrequest = FOIRawRequest.get_request(applicantpayload['rawrequestid'])
            raw_data = rawrequest["requestrawdata"]
            self.__update_applicant_data_on_raw_request(raw_data, applicantschema, applicantpayload['applicanttype'])
            result = rawrequestservice().saverawrequestversion(
                rawrequest['requestrawdata'],
                rawrequest['requestid'],
                rawrequest['assignedgroup'],
                rawrequest['assignedto'],
                rawrequest['status'], 
                userid,
                rawrequest['assignee.firstname'],
                rawrequest['assignee.middlename'],
                rawrequest['assignee.lastname'],
                rawrequest['requeststatuslabel']
            )
        return DefaultMethodResult(True,'Applicant profile created',applicantschema['foiRequestApplicantID'])

    def update_applicant_profile(self, applicantschema, applicantpayload, userid):
        applicanttype = applicantpayload.get("applicanttype")
        applicant = FOIRequestApplicant.from_applicant_data(applicantschema)
        save_result = FOIRequestApplicant.update_applicant_profile(applicant, applicantschema['foiRequestApplicantID'], userid)
        updated_applicant_id = save_result.identifier
        # foirequestapplicantid = applicantschema['foiRequestApplicantID']
        # updatedapplicant = FOIRequestApplicant.from_request_data(applicantschema)
        # applicant = FOIRequestApplicant.update_applicant_profile(updatedapplicant,foirequestapplicantid, userid) # replace with applicant id once new save function is written
        # applicantschema['foiRequestApplicantID'] = applicant.identifier
        requests = FOIMinistryRequest.getopenrequestsbyapplicantid(applicantschema['foiRequestApplicantID'])
        print('*requests: ', requests)
        applicanttype = applicantpayload.get("applicanttype")
        for request in requests:
            requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
            # requestschema.update(applicantschema)
            self.__update_applicant_data_on_request(requestschema, applicantschema, applicantpayload, "update")
            responseschema = requestservicecreate().saverequestversion(
                requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
            )
            if not responseschema.success:
                return responseschema

        rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicantschema['foiRequestApplicantID'])
        print('****rawrequests: ', requests)
        for rawrequest in rawrequests:
            
            self.__update_applicant_data_on_raw_request(rawrequest, applicantschema, applicanttype)
            rawrequestservice().saverawrequestversion(
                rawrequest['requestrawdata'],
                rawrequest['requestid'],
                rawrequest['assignedgroup'],
                rawrequest['assignedto'],
                rawrequest['status'], 
                userid,
                rawrequest['assignee.firstname'],
                rawrequest['assignee.middlename'],
                rawrequest['assignee.lastname'],
                rawrequest['requeststatuslabel']
            )
        return DefaultMethodResult(True,'Applicant profile updated',applicantschema['foiRequestApplicantID'])
    
    def reassignapplicantprofilelinkedtorequest(self, applicantschema, applicantpayload, userid):
        if applicantpayload['requesttype'] == 'foirequest':
            ministryrequest = FOIMinistryRequest.getopenrequestsbyrequestId([applicantpayload['foirequestid']])
            foirequestid = applicantpayload['foirequestid']
            foiministryrequestid = ministryrequest[0]['foiministryrequestid']
            requestschema = requestservicegetter().getrequest(foirequestid, foiministryrequestid)
            self.__update_applicant_data_on_request(requestschema, applicantschema, applicantpayload, "reassign")
            responseschema = requestservicecreate().saverequestversion(
                requestschema, foirequestid, foiministryrequestid, userid
            )
            if not responseschema.success:
                return responseschema
        elif applicantpayload['requesttype'] == 'rawrequest':
            rawrequest = FOIRawRequest.get_request(applicantpayload['rawrequestid'])
            raw_data = rawrequest["requestrawdata"]
            self.__update_applicant_data_on_raw_request(raw_data, applicantschema, applicantpayload['applicanttype'])
            rawrequestservice().saverawrequestversion(
                rawrequest['requestrawdata'],
                rawrequest['requestid'],
                rawrequest['assignedgroup'],
                rawrequest['assignedto'],
                rawrequest['status'], 
                userid,
                rawrequest['assignee.firstname'],
                rawrequest['assignee.middlename'],
                rawrequest['assignee.lastname'],
                rawrequest['requeststatuslabel']
            )
        return DefaultMethodResult(True,
                                   f"""Applicant Profile reassigned for {applicantpayload['requesttype']}""",
                                   applicantschema['foiRequestApplicantID'])
    
    def unassignapplicantprofilefromrequest(self, rawrequestid, userid):
        # For raw requests only
        rawrequest = FOIRawRequest.get_request(rawrequestid)
        ATTRIBUTES_TO_REMOVE = {
            'firstName', 'middleName', 'lastName', 'businessName', 'category',
            'foiRequestApplicantID', 'email', 'other_notes', 'phonePrimary', 'phoneSecondary',
            'workPhonePrimary', 'workPhoneSecondary', 'address', 'addressSecondary',
            'city', 'province', 'country', 'postal', 'correctionalServiceNumber',
            'publicServiceEmployeeNumber'
        }
        ADDITIONAL_INFO_FIELDS_TO_REMOVE = {'alsoKnownAs', 'birthDate', 'personalHealthNumber'}
        raw_data = rawrequest['requestrawdata']
        for key in ATTRIBUTES_TO_REMOVE:
            raw_data.pop(key, None)  # pop safely, no KeyError if missing
        additional_info = raw_data.get('additionalPersonalInfo')
        if additional_info:
            for key in ADDITIONAL_INFO_FIELDS_TO_REMOVE:
                additional_info.pop(key, None)
        rawrequestservice().saverawrequestversion(
            rawrequest['requestrawdata'],
            rawrequest['requestid'],
            rawrequest['assignedgroup'],
            rawrequest['assignedto'],
            rawrequest['status'], 
            userid,
            rawrequest['assignee.firstname'],
            rawrequest['assignee.middlename'],
            rawrequest['assignee.lastname'],
            rawrequest['requeststatuslabel']
        )
        return DefaultMethodResult(True,'Applicant profile unassigned from request',rawrequestid)

    def __validateandtransform(self, filterfields):
        return self.__transformfilteringfields(filterfields)

    def __transformfilteringfields(self, filterfields):
        return list(map(lambda x: x.replace('createdat', 'createdatformatted'), filterfields))

    def __first_not_null(self, _listoritem):
        if not isinstance(_listoritem, list):
            return _listoritem
        for item in _listoritem:
            if item is not None:
                return item
        return None

    def __prepareapplicant(self, applicant):
        return {
            'additionalPersonalInfo': {
                'alsoKnownAs': self.__first_not_null(applicant["alsoknownas"]),
                'birthDate': self.__first_not_null(applicant["dob"]),
                'personalHealthNumber': self.__first_not_null(applicant["phn"]),
            },
            'foiRequestApplicantID': self.__first_not_null(applicant["foirequestapplicantid"]),
            'applicantprofileid': self.__first_not_null(applicant["applicantprofileid"]),
            'firstName': self.__first_not_null(applicant["firstname"]),
            'middleName': self.__first_not_null(applicant["middlename"]),
            'lastName': self.__first_not_null(applicant["lastname"]),
            #'createdat' : self.__formatedate(applicant["createdat)"],
            'businessName': self.__first_not_null(applicant["businessname"]),
            # 'applicant': applicant["applicant"],
            # 'foirequestID': applicant["foirequestid"],
            # 'foirequestVersion': applicant["foirequestversion"],
            # 'requestType': applicant["requesttype"],
            'category': self.__first_not_null(applicant["applicantcategory"]),
            'email': self.__first_not_null(applicant["email"]),
            'address': self.__first_not_null(applicant["address"]),
            'addressSecondary': self.__first_not_null(applicant["address2"]),
            'city': self.__first_not_null(applicant["city"]),
            'province': self.__first_not_null(applicant["province"]),
            'postal': self.__first_not_null(applicant["postal"]),
            'country': self.__first_not_null(applicant["country"]),
            'phonePrimary': self.__first_not_null(applicant["homephone"]),
            'workPhonePrimary': self.__first_not_null(applicant["workphone"]),
            'workPhoneSecondary': self.__first_not_null(applicant["workphone2"]),
            'phoneSecondary': self.__first_not_null(applicant["mobilephone"]),           
            'otherContactInfo': self.__first_not_null(applicant["othercontactinfo"]),
            'publicServiceEmployeeNumber': self.__first_not_null(applicant["employeenumber"]),
            'correctionalServiceNumber': self.__first_not_null(applicant["correctionnumber"]),           
            'axisapplicantid': self.__first_not_null(applicant["axisapplicantid"]),
            'otherNotes': self.__first_not_null(applicant["other_notes"]),
            'requestHistory': applicant.get("requestHistory", None)
        }

    def getapplicanthistory(self, applicantid):
        applicantqueue = []

        # order by update date desc
        applicants = FOIRequestApplicant.getapplicanthistory(applicantid)
        if applicants is not None:
            newer = self.__prepareapplicantforcomparing(applicants[0])
            for idx, applicant in enumerate(applicants):
                cur = self.__prepareapplicantforcomparing(applicant)
                if(cur != newer):
                    updatedfields = dict(set(cur.items()) - set(newer.items()))
                    previousvalues = {} # store previous values for display
                    falsepositives = [] # store false positives where both values are None to remove after iteration
                    for key in updatedfields.keys():
                        previousvalues[key] = self.__getpreviousvalues(applicants, updatedfields[key], idx, key)
                        if previousvalues[key] is None and updatedfields[key] is None:
                            falsepositives.append(key)
                    for key in falsepositives:
                        del previousvalues[key]
                        del updatedfields[key]
                    if updatedfields != {}:
                        applicantqueue.append({ "updatedat": applicant['updatedat'], "createdby": applicant['createdby'], "fields": updatedfields, "previousvalues": previousvalues})
                    newer = cur
        return applicantqueue

    def __getpreviousvalues(self, applicants, updated_value, idx, key):
        n = 1
        while (idx + n) < len(applicants):
            older = self.__prepareapplicantforcomparing(applicants[idx + n])
            if older.get(key) != updated_value:
                return older.get(key)
            n += 1
        return None

    def __prepareapplicantforcomparing(self, applicant):
        return {
            'Also Known As': applicant["alsoknownas"],
            'Birth Date': applicant["dob"],
            'Personal Health Number': applicant["phn"],
            'First Name': applicant["firstname"],
            'Middle Name': applicant["middlename"],
            'Last Name': applicant["lastname"],
            'Organization': applicant["businessname"],
            'Other Notes': applicant["other_notes"],
            'Email': applicant["email"],
            'Address': applicant["address"],
            'City': applicant["city"],
            'Province': applicant["province"],
            'Postal Code': applicant["postal"],
            'Country': applicant["country"],
            'Home Phone': applicant["homephone"],
            'Work Phone': applicant["workphone"],
            'Alternative Phone': applicant["workphone2"],
            'Mobile Phone': applicant["mobilephone"],
            'Other Contact Info': applicant["othercontactinfo"],
            'Employee Number': applicant["employeenumber"],
            'Corrections Number': applicant["correctionnumber"],
            # 'Applicant Category': applicant["applicantcategory"],
        }

    def getapplicantrequests(self, applicantid):
        requestqueue = []

        # order by update date desc
        requests = FOIRequestApplicant.getapplicantrequests(applicantid)
        if requests is not None:
            for request in requests:
                requestqueue.append(self.__preparerequest(request))

        rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicantid)
        if rawrequests is not None:
            for request in rawrequests:
                requestqueue.append(self.__preparerawrequest(request))

        # Get historical requests from FOIRequestApplicant table
        applicant_profile = FOIRequestApplicant.get_applicant_profile_by_id(applicantid)
        request_history = applicant_profile.get("requestHistory")
        if request_history:
            for historical_request in request_history:
                requestqueue.append(self.__prepare_historical_request(historical_request, applicant_profile))
        return requestqueue

    def __preparerequest(self, request):
        return {
            'applicantprofileid': request["applicantprofileid"],
            'foirequestapplicantid': request["foirequestapplicantid"],
            'axisrequestid': request["axisrequestid"],
            'requestid': request["foirequest_id"],
            'ministryrequestid': request["foiministryrequestid"],
            'filenumber': request["filenumber"],
            'requeststatus': request["requeststatus"],
            'receiveddate': request["receiveddate"],
            'description': request["description"],
        }
    
    def __preparerawrequest(self, request):
        return {
            'foirequestapplicantid': request["requestrawdata"]['foiRequestApplicantID'],
            'axisrequestid': request["axisrequestid"],
            'filenumber': 'U-00' + str(request["requestid"]),
            'requestid': request["requestid"],
            'requeststatus': request["status"],
            'receiveddate': maya.parse(request["requestrawdata"]["receivedDate"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%b %d %Y').upper(),
            # 'receiveddate': request["requestrawdata"]["receivedDate"],
            'description': request["requestrawdata"]["description"],
        }

    def __prepare_historical_request(self, historical_request, applicant):
        return {
            'foirequestapplicantid': applicant["foirequestapplicantid"],
            'axisrequestid': historical_request["axisrequestid"],
            'requeststatus': historical_request["requeststatus"],
            'receiveddate': "Historical Request",
            'description': historical_request["description"],
        }

    def __update_child_data(self, requestschema, applicantschema):
        # requestschema["updatedFoiRequestChildApplicantID"] = applicantschema["foiRequestApplicantID"]
        requestschema["additionalPersonalInfo"]["childFirstName"] = applicantschema["firstName"]
        requestschema["additionalPersonalInfo"]["childMiddleName"] = applicantschema["middleName"]
        requestschema["additionalPersonalInfo"]["childLastName"] = applicantschema["lastName"]
        requestschema["additionalPersonalInfo"]["childBirthDate"] = applicantschema["additionalPersonalInfo"]["birthDate"]
        requestschema["additionalPersonalInfo"]["childAlsoKnownAs"] = applicantschema["additionalPersonalInfo"]["alsoKnownAs"]

    def __update_onbehalfof_data(self, requestschema, applicantschema):
        # requestschema["updatedFoiRequestOnBehalfOfApplicantID"] = applicantschema["foiRequestApplicantID"]
        requestschema["additionalPersonalInfo"]["anotherFirstName"] = applicantschema["firstName"]
        requestschema["additionalPersonalInfo"]["anotherMiddleName"] = applicantschema["middleName"]
        requestschema["additionalPersonalInfo"]["anotherLastName"] = applicantschema["lastName"]
        requestschema["additionalPersonalInfo"]["anotherBirthDate"] = applicantschema["additionalPersonalInfo"]["birthDate"]
        requestschema["additionalPersonalInfo"]["anotherAlsoKnownAs"] = applicantschema["additionalPersonalInfo"]["alsoKnownAs"]

    def __update_applicant_data_on_request(self, requestschema, applicantschema, applicantpayload, actiontype):
        if applicantpayload['applicanttype'] == "applicant":
            requestschema.update(applicantschema)
        elif applicantpayload['applicanttype'] == "child":
            self.__update_child_data(requestschema, applicantschema)
        elif applicantpayload['applicanttype'] == "onbehalfof":
            self.__update_onbehalfof_data(requestschema, applicantschema)
        
        requestschema["applicantdata"] = {
            "actiontype": actiontype, 
            "applicant": applicantschema,
            "applicanttype": applicantpayload['applicanttype'],
            "foirequestapplicantid": applicantschema["foiRequestApplicantID"]
        }
    
    def __update_applicant_data_on_raw_request(self, rawrequest, applicantschema, applicanttype):
        raw_data = rawrequest["requestrawdata"]
        if applicanttype == "applicant":
            rawrequest["foiRequestApplicantID"] = applicantschema["foiRequestApplicantID"]
            for key, value in applicantschema.items():
                if key != "additionalPersonalInfo":
                    raw_data[key] = value
            applicant_additional = applicantschema.get("additionalPersonalInfo")

            if applicant_additional:
                raw_data.setdefault("additionalPersonalInfo", {}).update(applicant_additional)
        if applicanttype == "child":
            rawrequest["foiRequestChildApplicantID"] = applicantschema["foiRequestApplicantID"]
            self.__update_child_data(raw_data, applicantschema)
        if applicanttype == "onbehalfof":
            rawrequest["foiRequestOnBehalfOfApplicantID"] = applicantschema["foiRequestApplicantID"]
            self.__update_onbehalfof_data(raw_data, applicantschema)