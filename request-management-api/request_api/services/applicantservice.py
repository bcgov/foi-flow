
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

    def __prepareapplicant(self, applicant):
        return {
            'additionalPersonalInfo': {
                'alsoKnownAs': applicant["alsoknownas"],
                'birthDate': applicant["dob"],
                'personalHealthNumber': applicant["phn"],
            },
            'foiRequestApplicantID': applicant["foirequestapplicantid"],
            'firstName': applicant["firstname"],
            'middleName': applicant["middlename"],
            'lastName': applicant["lastname"],
            #'createdat' : self.__formatedate(applicant["createdat)"],
            'businessName': applicant["businessname"],
            # 'applicant': applicant["applicant"],
            'applicantVersion': applicant["applicantversion"],
            'foirequestID': applicant["foirequestid"],
            'foirequestVersion': applicant["foirequestversion"],
            'requestType': applicant["requesttype"],
            'category': applicant["applicantcategory"],           
            'email':applicant["email"],
            'address': applicant["address"],
            'phonePrimary': applicant["homephone"],
            'workPhonePrimary': applicant["workphone"],
            'workPhoneSecondary': applicant["workphone2"],
            'phoneSecondary': applicant["mobilephone"],           
            'otherContactInfo':applicant["othercontactinfo"],
            'publicServiceEmployeeNumber': applicant["employeenumber"],
            'correctionalServiceNumber': applicant["correctionnumber"],           
        }
    