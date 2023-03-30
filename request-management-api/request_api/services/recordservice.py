
from os import stat, path,getenv
from re import VERBOSE
from request_api.utils.constants import FILE_CONVERSION_FILE_TYPES, DEDUPE_FILE_TYPES, NONREDACTABLE_FILE_TYPES
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
from request_api.services.records.recordservicegetter import recordservicegetter 
from request_api.services.records.recordservicebase import recordservicebase 

class recordservice(recordservicebase):
    """ FOI record management service
    """
    conversionstreamkey = getenv('EVENT_QUEUE_CONVERSION_STREAMKEY')
    dedupestreamkey = getenv('EVENT_QUEUE_DEDUPE_STREAMKEY')
    pdfstitchstreamkey = getenv('EVENT_QUEUE_PDFSTITCH_STREAMKEY')


    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)

    def fetch(self, requestid, ministryrequestid):
        return recordservicegetter().fetch(requestid, ministryrequestid)  
            
    def delete(self, requestid, ministryrequestid, recordid, userid):
        record = FOIRequestRecord.getrecordbyid(recordid)
        record['attributes'] = json.loads(record['attributes'])
        record.update({'updated_at': datetime.now(), 'updatedby': userid, 'isactive': False})
        record['version'] += 1
        newrecord = FOIRequestRecord()
        newrecord.__dict__.update(record)
        response = FOIRequestRecord.create([newrecord])
        if (response.success):
            _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/delete', {'ministryrequestid': ministryrequestid, 'filepaths': [record['s3uripath']]})
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, recordid)
            return DefaultMethodResult(True,'Record marked as inactive', -1, recordid)
        else:
            return DefaultMethodResult(False,'Error in deleting Record', -1, recordid)

    def retry(self, _requestid, ministryrequestid, data):
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        for record in data['records']:
            _filepath, extension = path.splitext(record['s3uripath'])
            if record['service'] == 'deduplication':
                if extension not in DEDUPE_FILE_TYPES:
                    return DefaultMethodResult(False,'Dedupe only accepts the following formats: ' + ', '.join(DEDUPE_FILE_TYPES), -1, record['recordid'])
                else:
                    streamkey = self.dedupestreamkey
            elif record['service'] == 'conversion':
                if extension not in FILE_CONVERSION_FILE_TYPES:
                    return DefaultMethodResult(False,'File Conversion only accepts the following formats: ' + ', '.join(FILE_CONVERSION_FILE_TYPES), -1, record['recordid'])
                else:
                    streamkey = self.conversionstreamkey
            jobids, err = self.makedocreviewerrequest('POST', '/api/jobstatus', {
                'records': [record],
                'batch': record['attributes']['batch'],
                'trigger': record['trigger'],
                'ministryrequestid': ministryrequestid
            })
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, ministryrequestid)
            streamobject = {
                "s3filepath": record['s3uripath'],
                "requestnumber": _ministryrequest['axisrequestid'],
                "bcgovcode": _ministryrequest['programarea.bcgovcode'],
                "filename": record['filename'],
                "ministryrequestid": ministryrequestid,
                "attributes": json.dumps(record['attributes']),
                "batch": record['attributes']['batch'],
                "jobid": jobids[record['s3uripath']]['jobid'],
                "documentmasterid": jobids[record['s3uripath']]['masterid'],
                "trigger": record['trigger'],
                "createdby": record['createdby']
            }
            if record.get('outputdocumentmasterid', False):
                streamobject['outputdocumentmasterid'] = record['outputdocumentmasterid']
            return eventqueueservice().add(streamkey, streamobject)
        
    def triggerpdfstitchservice(self, requestid, ministryrequestid, recordschema, userid):
        """Calls the BE job for stitching the documents.
        """
        return self.__triggerpdfstitchservice(requestid, ministryrequestid, recordschema, userid)
    
    def getpdfstitchpackagetodownload(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/pdfstitch/{0}/{1}'.format(ministryid, category))
        return response

    def getpdfstichstatus(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/pdfstitchjobstatus/{0}/{1}'.format(ministryid, category))
        if response is not None and len(response) > 0:
            return response.get("status")
        return ""

    def __triggerpdfstitchservice(self, requestid, ministryrequestid, message, userid):
        """Call the BE job for stitching the documents.
        """
        job, err = self.makedocreviewerrequest('POST', '/api/pdfstitchjobstatus', {
                "createdby": userid,
                "ministryrequestid": ministryrequestid,
                "inputfiles":message["attributes"],
                "category": message["category"]
            })
        print("job ========== ",job)
        print("jobid ========== ",job.get("id"))
        if err:
            return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, ministryrequestid)
        streamobject = {
            "jobid": job.get("id"),
            "category": message["category"],
            "requestnumber": message["requestnumber"],
            "bcgovcode": message["bcgovcode"],
            "createdby": userid,
            "requestid": requestid,
            "ministryrequestid": ministryrequestid,
            "attributes": json.JSONEncoder().encode(message["attributes"])
        }
        print("final message >>>>>> ", streamobject)
        return eventqueueservice().add(self.pdfstitchstreamkey, streamobject)

    def __bulkcreate(self, requestid, ministryrequestid, records, userid):
        """Creates bulk records for a user with document details passed in for an opened request.
        """
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        recordlist = []
        batch = str(uuid.uuid4())
        for entry in records:
            entry['attributes']['batch'] = batch
            _filepath, extension = path.splitext(entry['filename'])
            entry['attributes']['extension'] = extension
            entry['attributes']['incompatible'] =  extension in NONREDACTABLE_FILE_TYPES
            record = FOIRequestRecord(foirequestid=requestid, ministryrequestid = ministryrequestid, ministryrequestversion=_ministryversion,
                            version = 1, createdby = userid, created_at = datetime.now())
            record.__dict__.update(entry)
            recordlist.append(record)
        dbresponse = FOIRequestRecord.create(recordlist)
        if (dbresponse.success):
            #processingrecords = [{**record, **{"recordid": dbresponse.args[0][record['s3uripath']]['recordid']}} for record in records if not record['attributes'].get('incompatible', False)]
            processingrecords = [{**record, **{"recordid": dbresponse.args[0][record['s3uripath']]['recordid']}} for record in records]
           
            print(processingrecords)
            # record all jobs before sending first redis stream message to avoid race condition
            jobids, err = self.makedocreviewerrequest('POST', '/api/jobstatus', {
                'records': processingrecords,
                'batch': batch,
                'trigger': 'recordupload',
                'ministryrequestid': ministryrequestid
            })
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, ministryrequestid)
            # send message to redis stream for each file
            for entry in processingrecords:
                _filename, extension = path.splitext(entry['s3uripath'])
                if 'error' in jobids[entry['s3uripath']]:
                    logging.error("Doc Reviewer API was given an unsupported file type - no job triggered - Record ID: {0} File Name: {1} ".format(entry['recordid'], entry['filename']))
                else:
                    streamobject = {
                        "s3filepath": entry['s3uripath'],
                        "requestnumber": _ministryrequest['axisrequestid'],
                        "bcgovcode": _ministryrequest['programarea.bcgovcode'],
                        "filename": entry['filename'],
                        "ministryrequestid": ministryrequestid,
                        "attributes": json.dumps(entry['attributes']),
                        "batch": batch,
                        "jobid": jobids[entry['s3uripath']]['jobid'],
                        "documentmasterid": jobids[entry['s3uripath']]['masterid'],
                        "trigger": 'recordupload',
                        "createdby": userid,
                        "incompatible": 'true' if extension in NONREDACTABLE_FILE_TYPES else 'false'
                    }
                    if extension in FILE_CONVERSION_FILE_TYPES:
                        eventqueueservice().add(self.conversionstreamkey, streamobject)
                    if extension in DEDUPE_FILE_TYPES:
                        eventqueueservice().add(self.dedupestreamkey, streamobject)
        return dbresponse

    

    

    

