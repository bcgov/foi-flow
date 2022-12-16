
from os import stat, path,getenv
from re import VERBOSE
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.auth import auth, AuthHelper
import json
from datetime import datetime
import maya
import uuid
import requests
import logging
class recordservice:
    """ FOI record management service
    """
    tokenurl =  getenv("BPM_TOKEN_URL")
    docreviewerapiurl =  getenv("FOI_DOCREVIEWER_BASE_API_URL")

    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)

    def fetch(self, requestid, ministryrequestid):
        uploadedrecords = FOIRequestRecord.fetch(requestid, ministryrequestid)
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        divisions = FOIMinistryRequestDivision.getdivisions(ministryrequestid, _ministryversion)

        result = {}
        uploadedrecords = {record['s3uripath'] : {**record, **{"isdeduplicated": False, "isduplicate": False}} for record in uploadedrecords}
        dedupedrecords = []
        if len(uploadedrecords) > 0:
            token = AuthHelper.getauthtoken()
            response = requests.get(
                self.docreviewerapiurl+'/api/dedupestatus/{0}'.format(ministryrequestid),
                headers={'Authorization': token}
            )
            if response.status_code != 200:
                logging.error("Doc Reviewer API returned the following message: {0} - {1}".format(response.status_code, response.json()['description']))
            else:
                dedupedrecords = response.json()

        result['removedfiles'] = 0
        for dedupedrecord in dedupedrecords:
            print(type(dedupedrecord))
            record = uploadedrecords[dedupedrecord['filepath']]
            record['isdeduplicated'] = True
            record['isduplicate'] = dedupedrecord['isduplicate']
            record['attributes'] = dedupedrecord['attributes']
            if dedupedrecord['isduplicate']:
                result['removedfiles'] += 1
                record['duplicateof'] = dedupedrecord['duplicateof']
        result['records'] = self.__format(list(uploadedrecords.values()), divisions)
        result['dedupedfiles'] = len(dedupedrecords)
        # result['batchcount'] = len(set(map(lambda record: record['attributes']['batch'], result['records'])))
        result['batchcount'] = FOIRequestRecord.getbatchcount(ministryrequestid)
        return result


    def __bulkcreate(self, requestid, ministryrequestid, records, userid):
        """Creates bulk records for a user with document details passed in for an opened request.
        """
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        conversionstreamkey = getenv('EVENT_QUEUE_CONVERSION_STREAMKEY')
        dedupestreamkey = getenv('EVENT_QUEUE_DEDUPE_STREAMKEY')
        recordlist = []
        batch = str(uuid.uuid4())
        for entry in records:
            entry['attributes']['batch'] = batch
            record = FOIRequestRecord(foirequestid=requestid, ministryrequestid = ministryrequestid, ministryrequestversion=_ministryversion,
                            version = 1, createdby = userid, created_at = datetime.now())
            record.__dict__.update(entry)
            recordlist.append(record)
        dbresponse = FOIRequestRecord.create(recordlist)
        if (dbresponse.success):
            for entry in records:
                _filename, extension = path.splitext(entry['s3uripath'])
                if extension in ['.doc','.docx','.xls','.xlsx', '.ics', '.msg']:
                    eventqueueservice().add(conversionstreamkey, {"S3Path": entry['s3uripath']})
                if extension in ['.pdf']:
                    eventqueueservice().add(dedupestreamkey, {"s3filepath": entry['s3uripath'],
                    "requestnumber": _ministryrequest['axisrequestid'],
                     "bcgovcode": _ministryrequest['programarea.bcgovcode'],
                     "filename": entry['filename'],
                     "ministryrequestid": ministryrequestid,
                     "attributes": json.dumps(entry['attributes'])
                    })
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
        if isinstance(record['attributes'], str):
            record['attributes'] = json.loads(record['attributes'])
        attribute_divisions = record['attributes'].get('divisions')
        for division in attribute_divisions:
            division['divisionname'] = self.__getdivisionname(divisions, division['divisionid']).replace(u"’", u"'")
        record['attributes']['divisions'] = attribute_divisions
        return record

    def __getdivisionname(self, divisions, divisionid):
        for division in divisions:
            if division['division.divisionid'] == divisionid:
                return division['division.name']
        return None



