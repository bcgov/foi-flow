
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from datetime import datetime
import maya

class recordservice:
    """ FOI record management service
    """
    
    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)
        
    def fetch(self, requestid, ministryrequestid):
        records = FOIRequestRecord.fetch(requestid, ministryrequestid)
        return self.__formatcreateddate(records)

    
    def __bulkcreate(self, requestid, ministryrequestid, records, userid):
        """Creates bulk records for a user with document details passed in for an opened request.
        """
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        recordlist = []
        for entry in records:
            record = FOIRequestRecord(foirequestid=requestid, ministryrequestid = ministryrequestid, ministryrequestversion=_ministryversion, 
                            version = 1, createdby = userid, created_at = datetime.now())
            record.__dict__.update(entry)
            recordlist.append(record)
        return FOIRequestRecord.create(recordlist)


    def __formatcreateddate(self, records):
        for record in records:
            record = self.__pstformat(record)
        return records

    def __pstformat(self, record):
        formatedcreateddate = maya.parse(record['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        record['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        record['divisionname'] = record['divisionname'].replace(u"’", u"'")
        return record

