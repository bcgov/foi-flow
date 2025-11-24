
from os import path,getenv

from request_api.models.FOIRequestRecordHistory import FOIRequestRecordHistory
from request_api.utils import json_utils
from request_api.utils.constants import FILE_CONVERSION_FILE_TYPES, DEDUPE_FILE_TYPES, NONREDACTABLE_FILE_TYPES
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.HistoricalRecords import HistoricalRecords
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.models.default_method_result import DefaultMethodResult
from request_api.auth import AuthHelper
import json
from datetime import datetime
import maya
import uuid
import logging
from request_api.services.records.recordservicegetter import recordservicegetter 
from request_api.services.records.recordservicebase import recordservicebase
from sqlalchemy import inspect

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
    compressionstreamkey = getenv('EVENT_QUEUE_COMPRESSION_STREAMKEY')
    ocrstreamkey = getenv('EVENT_QUEUE_OCR_STREAMKEY')
    largefilecompressionstreamkey = getenv('EVENT_QUEUE_COMPRESSION_LARGE_FILE_STREAMKEY')
    largefileocrstreamkey = getenv('EVENT_QUEUE_OCR_LARGE_FILE_STREAMKEY')
    compressionlargefilesizelimit=getenv('COMPRESSION_STREAM_SEPARATION_FILE_SIZE_LIMIT',104857600)
    ocrlargefilesizelimit= getenv('OCR_STREAM_SEPARATION_FILE_SIZE_LIMIT',104857600)
    
    s3host = getenv('OSS_S3_HOST')

    DOC_REVIEWER_API_ERROR = 'Error in contacting Doc Reviewer API'

    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        records_list = recordschema.get("records", [])
        return self.__bulkcreate(requestid, ministryrequestid, records_list, userid)

    def fetch(self, requestid, ministryrequestid):
        return recordservicegetter().fetch(requestid, ministryrequestid)

    def get_all_records_by_divisionid(self, divisionid):
        return FOIRequestRecord.get_all_records_by_divisionid(divisionid)

    def _create_historical_record(self, record):
        """
        Creates and returns a detached FOIRequestRecordHistory instance
        by copying column values from the current FOIRequestRecord.
        """

        # 1. Create the new history instance
        history_record = FOIRequestRecordHistory()

        # 2. Copy data using a dictionary comprehension over mapped attributes
        #    We copy all column data from the source record.
        source_data = {
            column.key: getattr(record, column.key)
            for column in inspect(record.__class__).columns
        }

        history_record.__dict__.update(source_data)

        # 3. Explicitly reset the history table's primary key (id)
        history_record.id = None

        # 4. Set history-specific audit fields
        history_record.isactive = False
        history_record.updated_at = datetime.now()

        return history_record

    def _prepare_record_update(self, record, requestdata, userid):
        """Applies updates and version increment to the main ORM record."""


        # 1. Load the JSON string from the ORM object into a dictionary
        attributes_dict = json_utils.safe_json_loads(record.attributes)

        # 2. Update attributes
        if not requestdata['isdelete']:
            attributes_dict['divisions'] = [requestdata['divisions']]

        # 3. Save the modified dictionary back to the ORM object as a JSON string
        record.attributes = json.dumps(attributes_dict)

        # 4. Update core metadata
        record.updated_at = datetime.now()
        record.updatedby = userid
        record.isactive = not requestdata['isdelete']
        record.version += 1

        return record

    def _handle_doc_reviewer_api(self, ministryrequestid, records_data, requestdata):
        """Handles the external API call to the Doc Reviewer service."""

        if requestdata['isdelete']:
            endpoint = '/api/document/delete'
            payload = {
                'ministryrequestid': ministryrequestid,
                'filepaths': [r['filepath'] for r in records_data]
            }
        else:
            endpoint = '/api/document/update'
            payload = {
                'ministryrequestid': ministryrequestid,
                'documentmasterids': [r['documentmasterid'] for r in records_data],
                'divisions': requestdata['divisions']
            }

        _apiresponse, err = self.makedocreviewerrequest('POST', endpoint, payload)

        if err:
            doc_ids = [r['documentmasterid'] for r in records_data]
            return DefaultMethodResult(False, self.DOC_REVIEWER_API_ERROR, -1, doc_ids)

        success_msg = 'Record deleted in Doc Reviewer DB' if requestdata['isdelete'] else 'Record updated in Doc Reviewer DB'

        return DefaultMethodResult(True, success_msg, -1, [r['documentmasterid'] for r in records_data])

    def update(self, requestid, ministryrequestid, requestdata, userid):
        # 1. Input Validation and Retrieval
        records_data = requestdata['records']
        recordids = [r['recordid'] for r in records_data if r.get('recordid') is not None]

        if not recordids:
            return DefaultMethodResult(True, 'No records to update', -1, [])

        logging.debug(f"Updating records for ministry: {requestdata}")

        # 2. Preparation: History and Update Lists
        updated_orm_records = []
        historical_records = []

        if recordids:
            records = FOIRequestRecord.getrecordsbyid(recordids)

            for record in records:
                # History capture must occur BEFORE modification (version increment)
                historical_records.append(self._create_historical_record(record))

                # Apply all updates to the main record
                updated_record = self._prepare_record_update(record, requestdata, userid)
                updated_orm_records.append(updated_record)

            # 3. Database Transaction (Atomic Save)
            response = FOIRequestRecord.create(updated_orm_records, historical_records)

            if not response.success:
                doc_ids = [r['documentmasterid'] for r in records_data]
                return DefaultMethodResult(False, 'Error in updating Record', -1, doc_ids)

        # 4. External API Call
        return self._handle_doc_reviewer_api(ministryrequestid, records_data, requestdata)

    def _update_personal_attributes_dict(self, attributes_dict, new_personal_attributes):
        """
        Safely updates nested 'personalattributes' within the attributes dictionary.
        """
        if 'personalattributes' not in attributes_dict:
            attributes_dict['personalattributes'] = {}

        for attr, value in new_personal_attributes.items():
            # Check if the attribute value is valid (non-None and non-empty list/string)
            if value is not None and (isinstance(value, str) or isinstance(value, list)) and len(value) > 0:
                attributes_dict['personalattributes'][attr] = value

        return attributes_dict

    def _handle_doc_reviewer_api_personal(self, ministryrequestid, records_data, new_personal_attributes):
        """Handles the external API call to the Doc Reviewer service for personal attributes."""

        endpoint = '/api/document/update/personal'
        payload = {
            'ministryrequestid': ministryrequestid,
            'documentmasterids': [r['documentmasterid'] for r in records_data],
            'personalattributes': new_personal_attributes
        }

        _apiresponse, err = self.makedocreviewerrequest('POST', endpoint, payload)

        doc_ids = [r['documentmasterid'] for r in records_data]

        if err:
            return DefaultMethodResult(False, self.DOC_REVIEWER_API_ERROR, -1, doc_ids)

        return DefaultMethodResult(True, 'Record updated in Doc Reviewer DB', -1, doc_ids)

    def updatepersonalattributes(self, requestid, ministryrequestid, requestdata, userid):
        # 1. Initialization and Validation
        updated_orm_records = []
        historical_records = []
        records_data = requestdata['records']
        recordids = [r['recordid'] for r in records_data if r.get('recordid') is not None]

        if not recordids:
            return DefaultMethodResult(True, 'No records to update', -1, [])

        logging.info(f"Updating personal attributes for ministry: {requestdata}")

        # 2. Retrieval, History Capture, and Update
        records = FOIRequestRecord.getrecordsbyid(recordids)

        for record in records:
            # --- A. CAPTURE OLD STATE FOR HISTORY ---
            history_record = FOIRequestRecordHistory()
            mapper = inspect(record.__class__)
            for column in mapper.columns:
                if column.name != 'id':
                    setattr(history_record, column.name, getattr(record, column.name))

            history_record.isactive = False
            history_record.updated_at = datetime.now()
            historical_records.append(history_record)

            # Load, update, and save attributes
            attributes_dict = json_utils.safe_json_loads(record.attributes)

            attributes_dict = self._update_personal_attributes_dict(
                attributes_dict,
                requestdata['newpersonalattributes']
            )
            record.attributes = json.dumps(attributes_dict)  # Save modified dict back to ORM

            # Update core metadata fields
            record.updated_at = datetime.now()
            record.updatedby = userid
            record.version += 1

            # The record is modified; it's ready for merge.
            updated_orm_records.append(record)

        # 3. Database Transaction (Atomic Save)
        response = FOIRequestRecord.create(updated_orm_records, historical_records)

        if not response.success:
            doc_ids = [r['documentmasterid'] for r in records_data]
            return DefaultMethodResult(False, 'Error in updating Record', -1, doc_ids)

        # 4. External API Call
        return self._handle_doc_reviewer_api_personal(
            ministryrequestid,
            records_data,
            requestdata['newpersonalattributes']
        )


    def retry(self, _requestid, ministryrequestid, data):
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        for record in data['records']:
            _filepath, extension = path.splitext(record['s3uripath'])
            extension = extension.lower()            
            if record['service'] == 'deduplication':
                if extension not in DEDUPE_FILE_TYPES:
                    return DefaultMethodResult(False,'Dedupe only accepts the following formats: ' + ', '.join(DEDUPE_FILE_TYPES), -1, record['recordid'])
                else:
                    if ('convertedfilesize' in record['attributes'] and record['attributes']['convertedfilesize'] < int(self.dedupelargefilesizelimit) or 
                        'convertedfilesize' not in record['attributes'] and record['attributes']['filesize'] < int(self.dedupelargefilesizelimit)):
                        streamkey= self.dedupestreamkey
                    else:
                        streamkey= self.largefilededupestreamkey
            elif record['service'] == 'conversion':
                if extension not in FILE_CONVERSION_FILE_TYPES:
                    return DefaultMethodResult(False,'File Conversion only accepts the following formats: ' + ', '.join(FILE_CONVERSION_FILE_TYPES), -1, record['recordid'])
                else:
                    if record['attributes']['filesize'] < int(self.conversionlargefilesizelimit):
                        streamkey =self.conversionstreamkey
                    else:
                        streamkey =self.largefileconversionstreamkey
            elif record['service'] == 'compression':
                if extension not in (".pdf", ".jpg", ".jpeg"):
                    return DefaultMethodResult(False,'File Conversion only accepts the following formats: ' + ', '.join(FILE_CONVERSION_FILE_TYPES), -1, record['recordid'])
                else:
                    if ('convertedfilesize' in record['attributes'] and record['attributes']['convertedfilesize'] < int(self.compressionlargefilesizelimit) or 
                        'convertedfilesize' not in record['attributes'] and record['attributes']['filesize'] < int(self.compressionlargefilesizelimit)):
                        streamkey= self.compressionstreamkey
                    else:
                        streamkey= self.largefilecompressionstreamkey
            elif record['service'] == 'ocr':
                if extension != ".pdf":
                    return DefaultMethodResult(False,'File Conversion only accepts the following formats: ' + ', '.join(FILE_CONVERSION_FILE_TYPES), -1, record['recordid'])
                else:
                    if ('compressedfilesize' in record['attributes'] and record['attributes']['compressedfilesize'] < int(self.ocrlargefilesizelimit) or 
                        'compressedfilesize' not in record['attributes'] and record['attributes']['filesize'] < int(self.ocrlargefilesizelimit)):
                        streamkey = self.ocrstreamkey
                    else:
                        streamkey= self.largefileocrstreamkey
            else:
                streamkey = self.dedupestreamkey if extension in DEDUPE_FILE_TYPES else self.conversionstreamkey
            print("!!!!!!!",[record])
            jobids, err = self.makedocreviewerrequest('POST', '/api/jobstatus', {
                'records': [record],
                'batch': record['attributes']['batch'],
                'trigger': record['trigger'],
                'ministryrequestid': ministryrequestid
            })
            print("\njobids:",jobids)
            #print("\nERROR:",err)
            if err and err is not None:
                return DefaultMethodResult(False,self.DOC_REVIEWER_API_ERROR, -1, ministryrequestid)
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
                return DefaultMethodResult(False,self.DOC_REVIEWER_API_ERROR, -1, recordid)
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
                return DefaultMethodResult(False,self.DOC_REVIEWER_API_ERROR, -1, ministryrequestid)
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
        if (category == "redlinephase" or category == "responsepackagephase") and response is not None:
            for package in response:
                if "createdat" in package:
                    string_datetime = maya.parse(package["createdat"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p').upper()
                    package["createdat_datetime"] = string_datetime 
        elif response is not None and "createdat" in response:
            string_datetime = maya.parse(response["createdat"]).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y %b %d | %I:%M %p').upper()
            response["createdat_datetime"] = string_datetime
        return response

    def getpdfstichstatus(self, ministryid, category):
        response, err = self.makedocreviewerrequest('GET', '/api/pdfstitchjobstatus/{0}/{1}'.format(ministryid, category))
        if (category == "redlinephase" or category == "responsepackagephase") and response is not None:
            return json.dumps(response)
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
        if (len(documents) > 0 and documents[0]['iscorresponcedocument']):
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
                return DefaultMethodResult(False,self.DOC_REVIEWER_API_ERROR, -1, ministryrequestid)
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
        """
        Creates bulk records for a user with document details passed in for an opened request.
        Records are always created with version 1.
        """

        # 1. Retrieve necessary metadata
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        _ministryrequest = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        foirequestid = _ministryrequest.get('foirequest_id')

        recordlist = []
        batch = str(uuid.uuid4())
        now = datetime.now()

        # 2. Loop through entries and instantiate ORM objects safely
        for entry in records:
            # Prepare file-specific attributes
            entry['attributes']['batch'] = batch
            _filepath, extension = path.splitext(entry['filename'])
            entry['attributes']['extension'] = extension
            entry['attributes']['incompatible'] = extension.lower() in NONREDACTABLE_FILE_TYPES

            # 3. Define all ORM parameters, overriding defaults with dynamic data
            full_data = {
                # Dynamic data from 'entry' (filename, s3uripath, attributes, etc.)
                **entry,
                # Base metadata
                'foirequestid': foirequestid,
                'ministryrequestid': ministryrequestid,
                'ministryrequestversion': _ministryversion,
                'version': 1,
                'createdby': userid,
                'created_at': now,
                'isactive': True,  # Explicitly set status for new record
            }

            # 4. Instantiate the ORM object using safe keyword arguments
            try:
                record = FOIRequestRecord(**full_data)
                recordlist.append(record)
            except TypeError as e:
                logging.error(
                    f"Failed to create FOIRequestRecord instance for entry: {entry.get('filename')}. Error: {e}")
                raise

        # 5. Bulk Creation
        # Assumes FOIRequestRecord.create handles db.session.add_all(recordlist)
        dbresponse = FOIRequestRecord.bulk_create(recordlist)

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
                return DefaultMethodResult(False,self.DOC_REVIEWER_API_ERROR, -1, ministryrequestid)
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
        documentmasterids = requestdata["documentmasterids"]
        recordretrieveversion= requestdata["recordretrieveversion"]
        if(len(documentmasterids) > 0):
            _apiresponse, err = self.makedocreviewerrequest('POST', '/api/document/update/retrieveversion', {'ministryrequestid': ministryrequestid, 
                                            'documentmasterids': documentmasterids, "recordretrieveversion":recordretrieveversion})
            #print("_apiresponse:", _apiresponse)
            if err and err is not None:
                return DefaultMethodResult(False,f"Error in contacting Doc Reviewer API in retrieving record version - {err}", -1, ministryrequestid )
            return DefaultMethodResult(True,'Record version retrieved in Doc Reviewer DB ', -1, ministryrequestid)
        else:
            return DefaultMethodResult(False,'No records to retrieve record version', -1, ministryrequestid)

    

    

