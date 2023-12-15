
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.auth import AuthHelper
from dateutil import tz, parser
from flask import jsonify
from datetime import datetime as datetime2
from request_api.utils.commons.datetimehandler import datetimehandler
import re

class applicantservice:
    """ FOI Event Dashboard
    """

    def getapplicantbyemail(self, email):
        applicantqueue = []
        applicants = FOIRequestApplicant.getapplicantbyemail(email)
        print('applicants: ', applicants)
        if applicants is not None:
            for applicant in applicants:
                applicantqueue.append(self.__prepareapplicant(applicant))

        return applicantqueue

    def searchapplicant(self, keywords):
        applicantqueue = []
        applicants = FOIRequestApplicant.searchapplicant(keywords)
        if applicants is not None:
            for applicant in applicants:
                applicantqueue.append(self.__prepareapplicant(applicant))

        return applicantqueue

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
            'applicantVersion': applicant["applicantversion"],
            'foirequestID': applicant["foirequestid"],
            'foirequestVersion': applicant["foirequestversion"],
            'requestType': applicant["requesttype"],
            'category': applicant["applicantcategory"],           
            'email': self.__first_not_null(applicant["email"]),
            'address': self.__first_not_null(applicant["address"]),
            'phonePrimary': self.__first_not_null(applicant["homephone"]),
            'workPhonePrimary': self.__first_not_null(applicant["workphone"]),
            'workPhoneSecondary': self.__first_not_null(applicant["workphone2"]),
            'phoneSecondary': self.__first_not_null(applicant["mobilephone"]),           
            'otherContactInfo': self.__first_not_null(applicant["othercontactinfo"]),
            'publicServiceEmployeeNumber': self.__first_not_null(applicant["employeenumber"]),
            'correctionalServiceNumber': self.__first_not_null(applicant["correctionnumber"]),           
        }
    