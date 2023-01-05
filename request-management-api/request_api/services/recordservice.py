
from os import stat, path,getenv
from re import VERBOSE
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.models.default_method_result import DefaultMethodResult
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
    docreviewerapitimeout =  getenv("FOI_DOCREVIEWER_BASE_API_TIMEOUT")

    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)

    def fetch(self, requestid, ministryrequestid):
        uploadedrecords = FOIRequestRecord.fetch(requestid, ministryrequestid)
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        divisions = FOIMinistryRequestDivision.getdivisions(ministryrequestid, _ministryversion)

        result = {}
        uploadedrecords = {path.splitext(record['s3uripath'])[0] : {**record, **{"isdeduplicated": False, "isduplicate": False}} for record in uploadedrecords}
        result['removedfiles'] = 0
        if len(uploadedrecords) > 0:
            response, err = self.__makedocreviewerrequest('GET', '/api/dedupestatus/{0}'.format(ministryrequestid))
            if err is None:
                dedupedrecords = response['documents']
                for dedupedrecord in dedupedrecords:
                    if not dedupedrecord['isattachment']:
                        record = uploadedrecords[path.splitext(dedupedrecord['filepath'])[0]]
                        record['isdeduplicated'] = True
                        record['isduplicate'] = dedupedrecord['isduplicate']
                        record['attributes'] = dedupedrecord['attributes']
                        if dedupedrecord['isduplicate']:
                            record['duplicateof'] = dedupedrecord['duplicateof']
                    if dedupedrecord['isduplicate']:
                        result['removedfiles'] += 1
                # result['dedupedfiles'] = len(dedupedrecords)
                result['dedupedfiles'] = response['filesdeduped']
                result['convertedfiles'] = response['filesconverted']
                for failedrecord in (response['conversionerrors']):
                    record = uploadedrecords[path.splitext(failedrecord)[0]]
                    record['failed'] = 'conversion'
                for failedrecord in (response['dedupeerrors']):
                    record = uploadedrecords[path.splitext(failedrecord)[0]]
                    record['failed'] = 'deduplication'

        else:
            result.update({'dedupedfiles': 0, 'convertedfiles': 0})
        result['records'] = self.__format(list(uploadedrecords.values()), divisions)
        # result['batchcount'] = len(set(map(lambda record: record['attributes']['batch'], result['records'])))
        result['batchcount'] = FOIRequestRecord.getbatchcount(ministryrequestid)
        return result

    def delete(self, requestid, ministryrequestid, recordid, userid):
        record = FOIRequestRecord.getrecordbyid(recordid)
        record['attributes'] = json.loads(record['attributes'])
        record.update({'updated_at': datetime.now(), 'updatedby': userid, 'isactive': False})
        record['version'] += 1
        newrecord = FOIRequestRecord()
        newrecord.__dict__.update(record)
        response = FOIRequestRecord.create([newrecord])
        if (response.success):
            _apiresponse, err = self.__makedocreviewerrequest('POST', '/api/document/delete', {'filepath': record['s3uripath']})
            if err is None:
                return DefaultMethodResult(True,'Record marked as inactive', -1, recordid)
            else:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, recordid)
        else:
            return DefaultMethodResult(False,'Error in deleting Record', -1, recordid)

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
            # record all jobs before sending first redis stream message to avoid race condition
            jobids, err = self.__makedocreviewerrequest('POST', '/api/jobstatus', {'records': records, 'batch': batch, 'trigger': 'recordupload', 'ministryrequestid': ministryrequestid})
            print(jobids)
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, ministryrequestid)
            # send message to redis stream for each file
            for entry in records:
                _filename, extension = path.splitext(entry['s3uripath'])
                streamobject = {
                    "s3filepath": entry['s3uripath'],
                    "requestnumber": _ministryrequest['axisrequestid'],
                    "bcgovcode": _ministryrequest['programarea.bcgovcode'],
                    "filename": entry['filename'],
                    "ministryrequestid": ministryrequestid,
                    "attributes": json.dumps(entry['attributes']),
                    "batch": batch,
                    "jobid": jobids[entry['s3uripath']],
                    "trigger": 'recordupload',
                }
                if extension in ['.doc','.docx','.xls','.xlsx', '.ics', '.msg']:
                    eventqueueservice().add(conversionstreamkey, streamobject)
                if extension in ['.pdf']:
                    eventqueueservice().add(dedupestreamkey, streamobject)
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
        print("debug disappearing files")
        print(divisions)
        for division in divisions:
            print(division['division.divisionid'])
            print(divisionid)
            print(division['division.divisionid'] == divisionid)
            if division['division.divisionid'] == divisionid:
                return division['division.name']
        return None

    def __makedocreviewerrequest(self, method, url, payload=None):
        token = AuthHelper.getauthtoken()
        try:
            response = requests.request(
                method=method,
                url=self.docreviewerapiurl+url,
                data=json.dumps(payload),
                headers={'Authorization': token, 'Content-Type': 'application/json'},
                timeout=float(self.docreviewerapitimeout)
            )
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.HTTPError as err:
            logging.error("Doc Reviewer API returned the following message: {0} - {1}".format(err.response.status_code, err.response.text))
            return None, err
        except requests.exceptions.RequestException as err:
            logging.error(err)
            return None, err



