
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

    def getapplicantbyemail(self, email):
        applicantqueue = []
        applicants = FOIRequestApplicant.getapplicantbyemail(email)
        if applicants is not None:
            for applicant in applicants:
                applicantqueue.append(self.__prepareapplicant(applicant))

        return applicantqueue
    
    def getapplicantbyid(self, applicantid):
        applicant = FOIRequestApplicant.getapplicantbyid(applicantid)
        applicant = self.__prepareapplicant(applicant)
        applicant['requestHistory'] = self.getapplicantrequests(applicantid)
        return applicant

    def searchapplicant(self, keywords):
        applicantqueue = []
        applicants = FOIRequestApplicant.searchapplicant(keywords)
        if applicants is not None:
            for applicant in applicants:
                applicantqueue.append(self.__prepareapplicant(applicant))

        return applicantqueue
    
    def saveapplicantinfo(self, applicantschema, userid):
        applicant = FOIRequestApplicant.updateapplicantprofile(
            applicantschema['foiRequestApplicantID'],
            applicantschema['firstName'],
            applicantschema['lastName'],
            applicantschema['middleName'],
            applicantschema['businessName'],
            applicantschema.get('additionalPersonalInfo', None).get('alsoKnownAs', None),
            applicantschema.get('additionalPersonalInfo', None).get('birthDate', None),
            applicantschema['axisapplicantid'],
            userid
        ) # replace with applicant id once new save function is written
        # requests = FOIMinistryRequest.getopenrequestsbyrequestId(applicantschema['foirequestID'])
        applicantschema['foiRequestApplicantID'] = applicant.identifier
        requests = FOIMinistryRequest.getopenrequestsbyapplicantid(applicantschema['foiRequestApplicantID'])
        for request in requests:
            requestschema = requestservicegetter().getrequest(request['foirequest_id'], request['foiministryrequestid'])
            requestschema.update(applicantschema)
            responseschema = requestservicecreate().saverequestversion(
                requestschema, request['foirequest_id'], request['foiministryrequestid'], userid
            )
            if not responseschema.success:
                return responseschema
        rawrequests = FOIRawRequest.getrawrequestsbyapplicantid(applicantschema['foiRequestApplicantID'])
        for rawrequest in rawrequests:
            additionalPersonalInfo = rawrequest['requestrawdata'].get('additionalPersonalInfo', {}).update(applicantschema.get('additionalPersonalInfo', {}))
            rawrequest['requestrawdata'].update(applicantschema)
            rawrequest['requestrawdata']['additionalPersonalInfo'] = additionalPersonalInfo
            rawrequestservice().saverawrequestversion(
                rawrequest['requestrawdata'],
                rawrequest['requestid'],
                rawrequest['assignedgroup'],
                rawrequest['assignedto'],
                rawrequest['status'], 
                userid,
                rawrequest['assignee.firstname'],
                rawrequest['assignee.middlename'],
                rawrequest['assignee.lastname']
            )
        return DefaultMethodResult(True,'Applicant Info Updated',applicantschema['foiRequestApplicantID'])

    def __validateandtransform(self, filterfields):
        return self.__transformfilteringfields(filterfields)

    def __transformfilteringfields(self, filterfields):
        return list(map(lambda x: x.replace('createdat', 'createdatformatted'), filterfields))

    def __first_not_null(self, list):
        for item in list:
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
            'foiRequestApplicantID': applicant["foirequestapplicantid"],
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
        }

    def getapplicanthistory(self, applicantid):
        applicantqueue = []

        # order by update date desc
        applicants = FOIRequestApplicant.getapplicanthistory(applicantid)
        if applicants is not None:
            newer = self.__prepareapplicantforcomparing(applicants[0])
            updatedat = applicants[0]['updatedat']
            createdby = applicants[0]['createdby']
            for applicant in applicants:
                cur = self.__prepareapplicantforcomparing(applicant)
                if(cur != newer):
                    applicantqueue.append({ "updatedat": updatedat, "createdby": createdby, "fields": dict(set(cur.items()) - set(newer.items()))})
                    newer = cur
                updatedat = applicant['updatedat']
                createdby = applicant['createdby']

        return applicantqueue

    def __prepareapplicantforcomparing(self, applicant):
        return {
            'Also Known As': applicant["alsoknownas"],
            'Birth Date': applicant["dob"],
            'Personal Health Number': applicant["phn"],
            'First Name': applicant["firstname"],
            'Middle Name': applicant["middlename"],
            'Last Name': applicant["lastname"],
            'Organization': applicant["businessname"],
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
            'receiveddate': maya.parse(request["requestrawdata"]["receivedDate"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%^b %d %Y'),
            # 'receiveddate': request["requestrawdata"]["receivedDate"],
            'description': request["requestrawdata"]["description"],
        }