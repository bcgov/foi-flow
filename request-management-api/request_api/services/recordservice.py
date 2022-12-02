
from os import stat, path
from re import VERBOSE
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.external.eventqueueservice import eventqueueservice
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
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        divisions = FOIMinistryRequestDivision.getdivisions(ministryrequestid, _ministryversion)
        return self.__format(records, divisions)

    
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
        dbresponse = FOIRequestRecord.create(recordlist)
        # commented out for initial commit
        # if (dbresponse.success):
        #     for entry in records:
        #         _filename, extension = path.splitext(entry['s3uripath'])
        #         if extension in ['.doc','.docx','.xls','.xlsx', '.ics', '.msg']:
        #             eventqueueservice().add("file-conversion", {"S3Path": entry['s3uripath']})
        return dbresponse


    def __format(self, records, divisions):
        for record in records:
            record = self.__pstformat(record)
            record = self.__attributesformat(record, divisions)
        return records

    def __pstformat(self, record):
        formatedcreateddate = maya.parse(record['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        record['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        return record

    def __attributesformat(self, record, divisions):
        attributes = json.loads(record['attributes'])
        attribute_divisions = attributes.get('divisions')
        for division in attribute_divisions:
            division['divisionname'] = self.__getdivisionname(divisions, division['divisionid']).replace(u"’", u"'")
        record['attributes'] = attribute_divisions
        return record

    def __getdivisionname(self, divisions, divisionid):
        for division in divisions:
            if division['division.divisionid'] == divisionid:
                return division['division.name']
        return None



