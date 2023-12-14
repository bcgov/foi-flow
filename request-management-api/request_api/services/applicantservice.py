
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
            'foirequestapplicantid': applicant["foirequestapplicantid"],
            'firstname': applicant["firstname"],
            'middlename': applicant["middlename"],
            'lastname': applicant["lastname"],
            'alsoknownas': applicant["alsoknownas"],
            'dob' : applicant["dob"],
            #'createdat' : self.__formatedate(applicant["createdat)"],
            'businessname': applicant["businessname"],
            # 'applicant': applicant["applicant"],
            'applicantversion': applicant["applicantversion"],
            'foirequestid': applicant["foirequestid"],
            'foirequestversion': applicant["foirequestversion"],
            'requesttype': applicant["requesttype"],
            'applicantcategory': applicant["applicantcategory"],           
            'email':applicant["email"],
            'address': applicant["address"],
            'homephone': applicant["homephone"],
            'workphone': applicant["workphone"],
            'workphone2': applicant["workphone2"],
            'mobilephone': applicant["mobilephone"],           
            'othercontactinfo':applicant["othercontactinfo"],
            'employeenumber': applicant["employeenumber"],
            'correctionnumber': applicant["correctionnumber"],           
            'phn':applicant["phn"]
        }
    