
from os import stat, path,getenv
from re import VERBOSE
from request_api.utils.constants import FILE_CONVERSION_FILE_TYPES, DEDUPE_FILE_TYPES, NONREDACTABLE_FILE_TYPES
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.HistoricalRecords import HistoricalRecords
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
    largefileconversionstreamkey = getenv('EVENT_QUEUE_CONVERSION_LARGE_FILE_STREAM_KEY')
    dedupestreamkey = getenv('EVENT_QUEUE_DEDUPE_STREAMKEY')
    largefilededupestreamkey = getenv('EVENT_QUEUE_DEDUPE_LARGE_FILE_STREAMKEY')
    pdfstitchstreamkey = getenv('EVENT_QUEUE_PDFSTITCH_STREAMKEY')    
    dedupelargefilesizelimit= getenv('DEDUPE_STREAM_SEPARATION_FILE_SIZE_LIMIT',104857600)
    conversionlargefilesizelimit= getenv('CONVERSION_STREAM_SEPARATION_FILE_SIZE_LIMIT',3145728)
    stitchinglargefilesizelimit= getenv('STITCHING_STREAM_SEPARATION_FILE_SIZE_LIMIT',524288000)
    pdfstitchstreamkey_largefiles = getenv('EVENT_QUEUE_PDFSTITCH_LARGE_FILE_STREAMKEY')
    pagecalculatorstreamkey = getenv('EVENT_QUEUE_PAGECALCULATOR_STREAM_KEY')
    
    s3host = getenv('OSS_S3_HOST')

    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)

    def fetch(self, requestid, ministryrequestid):
        return recordservicegetter().fetch(requestid, ministryrequestid)

    def get_all_records_by_divisionid(self, divisionid):
        return FOIRequestRecord.get_all_records_by_divisionid(divisionid)  
            
    def update(self, requestid, ministryrequestid, requestdata, userid):
        newrecords = []
        recordids = [r['recordid'] for r in requestdata['records'] if r.get('recordid') is not None]
        response = DefaultMethodResult(True, 'No recordids')
        if(len(recordids) > 0):
            records = FOIRequestRecord.getrecordsbyid(recordids)
            for record in records:
                record['attributes'] = json.loads(record['attributes'])
                if not requestdata['isdelete']:
                    record['attributes']['divisions'] = requestdata['divisions']
                record.update({'updated_at': datetime.now(), 'updatedby': userid, 'isactive': not requestdata['isdelete']})
                record['version'] += 1
                newrecord = FOIRequestRecord()
                newrecord.__dict__.update(record)
                newrecords.append(newrecord)
            response = FOIRequestRecord.create(newrecords)
        if response.success:
            if requestdata['isdelete']:
                _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/delete', {'ministryrequestid': ministryrequestid, 'filepaths': [record['filepath'] for record in requestdata['records']]})
            else:
                _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/update', {'ministryrequestid': ministryrequestid, 'documentmasterids': [record['documentmasterid'] for record in requestdata['records']], 'divisions': requestdata['divisions']})
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1,  [record['documentmasterid'] for record in requestdata['records']])
            return DefaultMethodResult(True,'Record updated in Doc Reviewer DB', -1, [record['documentmasterid'] for record in requestdata['records']])
        else:
            return DefaultMethodResult(False,'Error in updating Record', -1, [record['documentmasterid'] for record in requestdata['records']])

    def updatepersonalattributes(self, requestid, ministryrequestid, requestdata, userid):
        newrecords = []
        recordids = [r['recordid'] for r in requestdata['records'] if r.get('recordid') is not None]
        response = DefaultMethodResult(True, 'No recordids')
        # divisions = []
        if(len(recordids) > 0):
            records = FOIRequestRecord.getrecordsbyid(recordids)
            for record in records:
                record['attributes'] = json.loads(record['attributes'])
                for attribute in requestdata['newpersonalattributes']:
                    if (requestdata['newpersonalattributes'][attribute] is not None and len(requestdata['newpersonalattributes'][attribute]) > 0):
                        if 'attributes' in record:
                            if 'personalattributes' in record['attributes']:
                                record['attributes']['personalattributes'][attribute] = requestdata['newpersonalattributes'][attribute]
                            else:
                                record['attributes']['personalattributes'] = {}
                        else:
                            record['attributes'] = {}
                            record['attributes']['personalattributes'] = {}
                        record['attributes']['personalattributes'][attribute] = requestdata['newpersonalattributes'][attribute]
                # divisions = divisions + [div for div in record['attributes']['divisions'] if div not in divisions]
                record.update({'updated_at': datetime.now(), 'updatedby': userid})
                record['version'] += 1
                newrecord = FOIRequestRecord()
                newrecord.__dict__.update(record)
                newrecords.append(newrecord)
            response = FOIRequestRecord.create(newrecords)
        if response.success:
            # _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/update', {'ministryrequestid': ministryrequestid, 'documentmasterids': [record['documentmasterid'] for record in requestdata['records']], 'divisions': divisions, 'personalattributes': requestdata['newpersonalattributes']})
            _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/update/personal', {'ministryrequestid': ministryrequestid, 'documentmasterids': [record['documentmasterid'] for record in requestdata['records']], 'personalattributes': requestdata['newpersonalattributes']})
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1,  [record['documentmasterid'] for record in requestdata['records']])
            return DefaultMethodResult(True,'Record updated in Doc Reviewer DB', -1, [record['documentmasterid'] for record in requestdata['records']])
        else:
            return DefaultMethodResult(False,'Error in updating Record', -1, [record['documentmasterid'] for record in requestdata['records']])

    def retry(self, _requestid, ministryrequestid, data):
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        for record in data['records']:
            _filepath, extension = path.splitext(record['s3uripath'])
            extension = extension.lower()            
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
            else:
                streamkey = self.dedupestreamkey if extension in DEDUPE_FILE_TYPES else self.conversionstreamkey
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
                "createdby": record['createdby'],
                "usertoken": AuthHelper.getauthtoken()
            }
            if record.get('outputdocumentmasterid', False):
                streamobject['outputdocumentmasterid'] = record['outputdocumentmasterid']
            if record['trigger'] == 'recordreplace' and record['attributes']['isattachment'] == True:
                streamobject['originaldocumentmasterid'] = record['documentmasterid']
            return eventqueueservice().add(streamkey, streamobject)

    def replace(self, _requestid, ministryrequestid, recordid, recordschema, userid):
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        recordlist = []
        records = recordschema.get("records")
        for _record in records:
            replacingrecord = FOIRequestRecord.getrecordbyid(recordid)           
            _delteeapiresponse, err = self.makedocreviewerrequest('POST', '/api/document/delete', {'ministryrequestid': ministryrequestid, 'filepaths': [replacingrecord['s3uripath']]})
            
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1, recordid)
            record = FOIRequestRecord(foirequestid=_requestid, replacementof = recordid if _record['replacementof'] is None else _record['replacementof'], ministryrequestid = ministryrequestid, ministryrequestversion=_ministryversion,
                                version = 1, createdby = userid, created_at = datetime.now())
            batch = str(uuid.uuid4())
            _record['attributes']['batch'] = batch
            _record['attributes']['lastmodified'] = json.loads(replacingrecord['attributes'])['lastmodified']
            _filepath, extension = path.splitext(_record['filename'])
            _record['attributes']['extension'] = extension            
            _record['attributes']['incompatible'] =  extension.lower() in NONREDACTABLE_FILE_TYPES 
            record.__dict__.update(_record)
            recordlist.append(record)
        dbresponse = FOIRequestRecord.replace(recordid,recordlist)
        if (dbresponse.success):
            processingrecords = [{**record, **{"recordid": dbresponse.args[0][record['s3uripath']]['recordid']}} for record in records]
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
                extension = extension.lower()
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
                        "incompatible": 'true' if extension in NONREDACTABLE_FILE_TYPES else 'false',
                        "usertoken": AuthHelper.getauthtoken()
                    }
                    if extension in FILE_CONVERSION_FILE_TYPES:
                        eventqueueservice().add(self.conversionstreamkey, streamobject)
                    if extension in DEDUPE_FILE_TYPES:
                        eventqueueservice().add(self.dedupestreamkey, streamobject)
        return dbresponse

    def triggerpdfstitchservice(self, requestid, ministryrequestid, recordschema, userid):
        """Calls the BE job for stitching the documents.
        """
        return self.__triggerpdfstitchservice(requestid, ministryrequestid, recordschema, userid)
    
    def getpdfstitchpackagetodownload(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/pdfstitch/{0}/{1}'.format(ministryid, category))
        if response is not None and "createdat" in response:
            string_datetime = maya.parse(response["createdat"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p').upper()
            response["createdat_datetime"] = string_datetime
        return response

    def getpdfstichstatus(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/pdfstitchjobstatus/{0}/{1}'.format(ministryid, category))
        if response is not None and "status" in response:
            return response.get("status")
        return ""

    def isrecordschanged(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/recordschanged/{0}/{1}'.format(ministryid, category))
        if response is None:
                return {"recordchanged": False}
        return response
    
    def gethistoricaldocuments(self, axisrequestid):
        documents = HistoricalRecords.getdocuments(axisrequestid)
        if (documents[0]['iscorresponcedocument']):
            for document in documents:
                if len(document['attributes']) > 0:
                    document['category'] = 'response'
                document['documentpath'] = 'https://' + self.s3host + '/' + document.pop('s3uripath') + '/' + document.pop('recordfilename')
                document['filename'] = document.pop('displayfilename')
            return documents
        else:
            for document in documents:
                document['s3uripath'] = 'https://' + self.s3host + '/' + document['s3uripath'] + '/' + document.pop('recordfilename')
                document['filename'] = document.pop('displayfilename')
                document['isselected'] = False
                document['isredactionready'] = True
                document['documentmasterid'] = document['historicalrecordid']
            return {'records': documents, 'dedupedfiles': len(documents), 'convertedfiles': 0, 'removedfiles': 0}

            

    def __triggerpdfstitchservice(self, requestid, ministryrequestid, message, userid):
        """Call the BE job for stitching the documents.
        """
        if self.pdfstitchstreamkey_largefiles or self.pdfstitchstreamkey:
            job, err = self.makedocreviewerrequest('POST', '/api/pdfstitchjobstatus', {
                    "createdby": userid,
                    "ministryrequestid": ministryrequestid,
                    "inputfiles":message["attributes"],
                    "category": message["category"]
                })
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
                "attributes": json.JSONEncoder().encode(message["attributes"]),
                "totalfilesize": message["totalfilesize"]
            }
            if message["totalfilesize"] > int(self.stitchinglargefilesizelimit) and self.pdfstitchstreamkey_largefiles:
                return eventqueueservice().add(self.pdfstitchstreamkey_largefiles, streamobject)
            elif self.pdfstitchstreamkey:
                return eventqueueservice().add(self.pdfstitchstreamkey, streamobject)
        else:
            print("pdfstitch stream key is missing. Message is not pushed to the stream.")
            return DefaultMethodResult(False,'pdfstitch stream key is missing. Message is not pushed to the stream.', -1, ministryrequestid)

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
            entry['attributes']['incompatible'] =  extension.lower() in NONREDACTABLE_FILE_TYPES
            record = FOIRequestRecord(foirequestid=_ministryrequest['foirequest_id'], ministryrequestid = ministryrequestid, ministryrequestversion=_ministryversion,
                            version = 1, createdby = userid, created_at = datetime.now())
            record.__dict__.update(entry)
            recordlist.append(record)
        dbresponse = FOIRequestRecord.create(recordlist)
        if (dbresponse.success):
            #processingrecords = [{**record, **{"recordid": dbresponse.args[0][record['s3uripath']]['recordid']}} for record in records if not record['attributes'].get('incompatible', False)]
            processingrecords = [{**record, **{"recordid": dbresponse.args[0][record['s3uripath']]['recordid']}} for record in records]

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
                extension = extension.lower()
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
                        "incompatible": 'true' if extension in NONREDACTABLE_FILE_TYPES else 'false',
                        "usertoken": AuthHelper.getauthtoken(),
                    }
                    if extension in FILE_CONVERSION_FILE_TYPES:
                        if entry['attributes']['filesize'] < int(self.conversionlargefilesizelimit):
                            assignedstreamkey =self.conversionstreamkey
                        else:
                            assignedstreamkey =self.largefileconversionstreamkey
                        eventqueueservice().add(assignedstreamkey, streamobject)
                    if extension in DEDUPE_FILE_TYPES:
                        if 'convertedfilesize' in entry['attributes'] and entry['attributes']['convertedfilesize'] < int(self.dedupelargefilesizelimit) or 'convertedfilesize' not in entry['attributes'] and entry['attributes']['filesize'] < int(self.dedupelargefilesizelimit):
                            assignedstreamkey= self.dedupestreamkey
                        else:
                            assignedstreamkey= self.largefilededupestreamkey
                        eventqueueservice().add(assignedstreamkey, streamobject)
        return dbresponse
    
    # this is for inflight request pagecount calculation option 1
    async def updatepagecount(self, ministryrequestid, userid):
        streamobj = {
            'ministryrequestid': ministryrequestid
        }
        job, err = self.makedocreviewerrequest('POST', '/api/pagecalculatorjobstatus', streamobj)
        if err:
            return DefaultMethodResult(False,'Error in contacting Doc Reviewer API for pagecalculatorjobstatus', -1, ministryrequestid)
        else:
            streamobj["jobid"] = job.get("id")
            streamobj["createdby"] = userid
        eventqueueservice().add(self.pagecalculatorstreamkey, streamobj)
        return DefaultMethodResult(True,'Pushed to PageCountCalculator stream', job.get("id"), ministryrequestid)
    
    # this is for inflight request pagecount calculation option 2
    async def calculatepagecount(self, requestid, ministryrequestid, userid):
        uploadedrecords = FOIRequestRecord.fetch(requestid, ministryrequestid)
        if len(uploadedrecords) > 0:
          records, err = recordservicegetter().getdatafromdocreviewer(uploadedrecords, ministryrequestid)
          if err is None:
            pagecount = self.__calculatepagecount(records)
            return FOIMinistryRequest().updaterecordspagecount(ministryrequestid, pagecount, userid) 
        return DefaultMethodResult(True,'No request to update', ministryrequestid)
    
    # this is for inflight request pagecount calculation option 2
    def __calculatepagecount(self, records):
        print(f'records = {records}')
        page_count = 0
        for record in records:
            if self.__pagecountcalculationneeded(record):
                page_count += record.get("pagecount", 0)
                attachments = record.get("attachments", [])
                for attachment in attachments:
                    if not attachment.get("isduplicate", False):
                        page_count += attachment.get("pagecount", 0)
        return page_count

    def __pagecountcalculationneeded(self, record):
        if not record.get("isduplicate", False) and not record["attributes"].get("isportfolio", False) and not record['attributes'].get('incompatible', False):
            return True
        return False
    
    def retrieverecordbyprocessversion(self, requestid, ministryrequestid, requestdata, userid):
        recordids = requestdata["recordids"]
        recordretrieveversion= requestdata["recordretrieveversion"]
        if(len(recordids) > 0):
            _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/update/retrieveversion', {'ministryrequestid': ministryrequestid, 
                                            'recordids': recordids, "recordretrieveversion":recordretrieveversion})
            if err:
                return DefaultMethodResult(False,'Error in contacting Doc Reviewer API', -1,  [record['documentmasterid'] for record in requestdata['records']])
            return DefaultMethodResult(True,'Record updated in Doc Reviewer DB', -1, [record['documentmasterid'] for record in requestdata['records']])
        else:
            return DefaultMethodResult(False,'Error in updating Record', -1, [record['documentmasterid'] for record in requestdata['records']])

    

    

