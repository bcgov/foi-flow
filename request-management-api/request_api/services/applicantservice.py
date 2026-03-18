
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
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
        applicanttype = applicantpayload.get('applicanttype')

        applicant = FOIRequestApplicant.from_request_data(applicantschema, is_new=True)
        save_result = FOIRequestApplicant.save_instance(applicant, userid)
        applicantschema['foiRequestApplicantID'] = save_result.identifier
        if applicantpayload.get('foirequestid', None) and requesttype == 'foirequest':
            requests = FOIMinistryRequest.getopenrequestsbyrequestId([applicantpayload['foirequestid']])
            for request in requests:
                print('\n\n**SETTING NEW APPLICANT FOR REQUEST: ', request, '\n\n')
                requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
                self.__update_requestschema(requestschema, applicantschema, applicanttype)
                responseschema = requestservicecreate().saverequestversion(
                    requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
                )
                if not responseschema.success:
                    return responseschema

        if applicantpayload.get('rawrequestid', None) and requesttype == 'rawrequest':
            rawrequest = FOIRawRequest.get_request(applicantpayload['rawrequestid'])
            raw_data = rawrequest["requestrawdata"]
            print('\n\n**SETTING NEW APPLICANT FOR RAW REQUEST ID: ', applicantpayload['rawrequestid'], '\n\n')
            self.__update_requestschema(raw_data, applicantschema, applicantpayload["applicanttype"])
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
        return DefaultMethodResult(True,'Applicant profile created',applicantschema['foiRequestApplicantID'])

    def update_applicant_profile(self, applicantschema, applicantpayload, userid):
        applicant_id_before_update = applicantschema['foiRequestApplicantID']

        updatedapplicant = FOIRequestApplicant.from_request_data(applicantschema)
        applicant = FOIRequestApplicant.save_instance(updatedapplicant, userid)
        applicantschema['foiRequestApplicantID'] = applicant.identifier

        primary_requests = FOIMinistryRequest.getopenrequestsbyapplicantid(applicant_id_before_update, "applicant")
        onbehalfof_requests = FOIMinistryRequest.getopenrequestsbyapplicantid(applicant_id_before_update, "onbehalfof")
        updated_primary_requests = []
        updated_onbehalfof_requests = []
        for request in primary_requests:
            requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
            self.__update_requestschema(requestschema, applicantschema, "applicant")
            responseschema = requestservicecreate().saverequestversion(
                requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
            )
            updated_primary_requests.append(requestschema.get("axisRequestId"))
            if not responseschema.success:
                return responseschema
        for request in onbehalfof_requests:
            requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
            self.__update_requestschema(requestschema, applicantschema, "onbehalfof")
            responseschema = requestservicecreate().saverequestversion(
                requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
            )
            updated_onbehalfof_requests.append(requestschema.get("axisRequestId"))
            if not responseschema.success:
                return responseschema

        primary_rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicant_id_before_update, "applicant")
        onbehalfof_rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicant_id_before_update, "onbehalfof")
        for rawrequest in primary_rawrequests:
            raw_data = rawrequest["requestrawdata"]
            self.__update_requestschema(raw_data, applicantschema, "applicant")
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
            updated_primary_requests.append(rawrequest.get("axisrequestid"))
        for rawrequest in onbehalfof_rawrequests:
            raw_data = rawrequest["requestrawdata"]
            self.__update_requestschema(raw_data, applicantschema, "onbehalfof")
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
            updated_onbehalfof_requests.append(rawrequest.get("axisrequestid"))
        update_message = f'Updated primary applicant requests: {", ".join(updated_primary_requests)}. \n' \
        'Updated onbehalfof applicant on: f{", ".join(updated_onbehalfof_requests)}'
        return DefaultMethodResult(True, update_message, applicantschema['foiRequestApplicantID'])
    
    def reassignapplicantprofilelinkedtorequest(self, applicantschema, applicantpayload, userid):
        if applicantpayload['requesttype'] == 'foirequest':
            ministryrequest = FOIMinistryRequest.getopenrequestsbyrequestId([applicantpayload['foirequestid']])
            foirequestid = applicantpayload['foirequestid']
            foiministryrequestid = ministryrequest[0]['foiministryrequestid']
            print('\n***REASSIGNING MINISTRY REQUEST: ', ministryrequest)
            requestschema = requestservicegetter().getrequest(foirequestid, foiministryrequestid)
            self.__update_requestschema(requestschema, applicantschema, applicantpayload["applicanttype"])
            responseschema = requestservicecreate().saverequestversion(
                requestschema, foirequestid, foiministryrequestid, userid
            )
            if not responseschema.success:
                return responseschema
        elif applicantpayload['requesttype'] == 'rawrequest':
            rawrequest = FOIRawRequest.get_request(applicantpayload['rawrequestid'])
            raw_data = rawrequest["requestrawdata"]
            print('\n***REASSIGNING RAW REQUEST: ', rawrequest)
            self.__update_requestschema(raw_data, applicantschema, applicantpayload["applicanttype"])
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
        requests = FOIRequestApplicant.getapplicantrequests(applicantid, "all")
        if requests is not None:
            for request in requests:
                requestqueue.append(self.__preparerequest(request))

        rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicantid, "all")
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

    def __update_requestschema(self, requestschema, applicantschema, applicanttype):
        if applicanttype == "onbehalfof":
            requestschema["foiRequestOnBehalfOfApplicantID"] = applicantschema.get("foiRequestApplicantID")
            additional = requestschema.get("additionalPersonalInfo")
            if additional:
                additional["anotherFirstName"] = applicantschema.get("firstName")
                additional["anotherMiddleName"] = applicantschema.get("middleName")
                additional["anotherLastName"] = applicantschema.get("lastName")
                additional["anotherBirthDate"] = applicantschema.get("additionalPersonalInfo", {}).get("birthDate")
                additional["anotherAlsoKnownAs"] = applicantschema.get("additionalPersonalInfo", {}).get("alsoKnownAs")
        if applicanttype == "applicant":
            additional = requestschema.get("additionalPersonalInfo")
            requestschema.update({
                k: v for k, v in applicantschema.items()
                if k != "additionalPersonalInfo"
            })
            if additional:
                additional["birthDate"] = applicantschema.get("additionalPersonalInfo", {}).get("birthDate")
                additional["alsoKnownAs"] = applicantschema.get("additionalPersonalInfo", {}).get("alsoKnownAs")
                additional["personalHealthNumber"] = applicantschema.get("additionalPersonalInfo", {}).get("personalHealthNumber")