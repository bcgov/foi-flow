
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
import copy

class recordservice:
    """ FOI record management service
    """
    tokenurl =  getenv("BPM_TOKEN_URL")
    docreviewerapiurl =  getenv("FOI_DOCREVIEWER_BASE_API_URL")
    docreviewerapitimeout =  getenv("FOI_DOCREVIEWER_BASE_API_TIMEOUT")
    conversionstreamkey = getenv('EVENT_QUEUE_CONVERSION_STREAMKEY')
    dedupestreamkey = getenv('EVENT_QUEUE_DEDUPE_STREAMKEY')

    def create(self, requestid, ministryrequestid, recordschema, userid):
        """Creates a record for a user with document details passed in for an opened request.
        """
        return self.__bulkcreate(requestid, ministryrequestid, recordschema.get("records"), userid)

    def fetch(self, requestid, ministryrequestid):
        result = {'dedupedfiles': 0, 'convertedfiles': 0, 'removedfiles': 0, 'records':[]}
        _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        divisions = FOIMinistryRequestDivision.getdivisions(ministryrequestid, _ministryversion)
        uploadedrecords = FOIRequestRecord.fetch(requestid, ministryrequestid)
        batchids = []
        resultrecords = []
        if len(uploadedrecords) > 0:
            computingresponses, err = self.__makedocreviewerrequest('GET', '/api/dedupestatus/{0}'.format(ministryrequestid))
            if err is None: 
                _convertedfiles, _dedupedfiles, _removedfiles = self.__getcomputingsummary(computingresponses)
                for record in uploadedrecords:
                    _computingresponse = self.__getcomputingresponse(computingresponses, "recordid", record)
                    _record = self.__preparerecord(record,_computingresponse, computingresponses,divisions)
                    resultrecords.append(_record)
                    if record["batchid"] not in batchids:
                        batchids.append(record["batchid"])  
                resultrecords = self.__handleduplicate(resultrecords)  
                result["convertedfiles"] =  _convertedfiles
                result["dedupedfiles"] = _dedupedfiles
                result["removedfiles"] =  _removedfiles 
            result['batchcount'] = len(batchids)
            result["records"] = resultrecords
        return result  
            
    def __preparerecord(self, record, _computingresponse, computingresponses, divisions):
        _record = self.__pstformat(record)
        documentmasterid = _computingresponse["documentmasterid"]
        _record['isduplicate'] = _computingresponse['isduplicate']
        _record['attributes'] = self.__formatrecordattributes(_computingresponse['attributes'], divisions)
        _record['isredactionready'] = _computingresponse['isredactionready']
        _record['trigger'] = _computingresponse['trigger']
        _record['documentmasterid'] = _computingresponse["documentmasterid"]
        _record['outputdocumentmasterid'] = documentmasterid 
        _record['attachments'] = []
        if _computingresponse['isduplicate']:
            _record['duplicatemasterid'] = _computingresponse['duplicatemasterid']  
            _record['duplicateof'] = _computingresponse['duplicateof']    
        attachment_list = self.__getcomputingresponse(computingresponses, "parentid", documentmasterid)
        for attachment in attachment_list:
            _attachement = self.__pstformat(attachment)
            _attachement['isattachment'] = True
            _attachement['s3uripath'] = attachment['filepath']
            _attachement['rootparentid'] = record["recordid"]
            _attachement['createdby'] = record['createdby']
            _attachement['attributes'] = self.__formatrecordattributes(attachment['attributes'], divisions)
            _record['attachments'].append(_attachement)                      
        _computingresponse_err = self.__getcomputingerror(_computingresponse)
        if _computingresponse_err is not None:
            record['failed'] = _computingresponse_err                
        return _record
    
    def __formatrecordattributes(self, attributes, divisions):
        if isinstance(attributes, str):
            attributes = json.loads(attributes)
        attribute_divisions = attributes.get('divisions', [])
        for division in attribute_divisions:
            _divisionname = self.__getdivisionname(divisions, division['divisionid'])
            division['divisionname'] = _divisionname.replace(u"’", u"'") if _divisionname is not None else ''
        return attributes    
    
    def __handleduplicate(self, resultrecords):        
        _resultrecords = copy.deepcopy(resultrecords)
        for result in resultrecords:
            if result["isduplicate"] == True:
                _resultrecords = self.__mergeduplicatedivisions(resultrecords, result["duplicatemasterid"], self.__getrecorddivisions(result["attributes"]) )
            _attachments = result["attachments"]
            for attachment in _attachments:
                if attachment["isduplicate"] == True:
                    _resultrecords = self.__mergeduplicatedivisions(resultrecords, attachment["duplicatemasterid"], self.__getrecorddivisions(attachment["attributes"]))
        return _resultrecords              


    def __mergeduplicatedivisions(self, _resultrecords, duplicatemasterid, divisions):
        for entry in _resultrecords:
            if int(entry["documentmasterid"]) == int(duplicatemasterid):
                resultattributes = entry["attributes"]
                resultattributes["divisions"] = self.__getrecorddivisions(resultattributes) + divisions 
            _attachments = entry["attachments"]
            for attachment in _attachments:
                if int(attachment["documentmasterid"]) == int(duplicatemasterid): 
                    attattributes = attachment["attributes"]
                    attattributes["divisions"] = self.__getrecorddivisions(attattributes) + divisions    
        return _resultrecords
    
    def __getrecorddivisions(self, _attributes):
        if isinstance(_attributes, str):
            _attributes = json.loads(_attributes)  
        return _attributes.get('divisions', [])  

    def __getcomputingresponse(self, response, filterby, data: any):
        if filterby == "recordid":
            filtered_response = [x for x in response if x["recordid"] == data["recordid"] and x["filename"] == data["filename"]]
            return filtered_response[0]
        else:
            filtered_response = [x for x in response if x[filterby] == data]
            return filtered_response

    def __getcomputingerror(self, computingresponse):
        if computingresponse['conversionstatus'] == 'error':
            return 'conversion' 
        elif computingresponse['deduplicationstatus'] == 'error':
            return 'deduplication'  
        return None 
    
    def __getcomputingsummary(self, computingresponse):
        _convertedfiles = _dedupedfiles = _removedfiles = 0
        for entry in computingresponse:
            if entry["conversionstatus"] == "completed":
                _convertedfiles += 1 
            if entry["deduplicationstatus"] == "completed":
                _dedupedfiles += 1 
            if entry["isduplicate"] == True:
                _removedfiles += 1 
        return _convertedfiles, _dedupedfiles, _removedfiles
                
    
    def delete(self, requestid, ministryrequestid, recordid, userid):
        record = FOIRequestRecord.getrecordbyid(recordid)
        record['attributes'] = json.loads(record['attributes'])
        record.update({'updated_at': datetime.now(), 'updatedby': userid, 'isactive': False})
        record['version'] += 1
        newrecord = FOIRequestRecord()
        newrecord.__dict__.update(record)
        response = FOIRequestRecord.create([newrecord])
        if (response.success):
            if (not record['attributes'].get('incompatible', False)):
                _apiresponse, err = self.__makedocreviewerrequest('POST', '/api/document/delete', {'filepaths': [record['s3uripath']]})
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
            jobids, err = self.__makedocreviewerrequest('POST', '/api/jobstatus', {
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
            jobids, err = self.__makedocreviewerrequest('POST', '/api/jobstatus', {
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
                    print('alert:reached DEDUPE event condition')
                    eventqueueservice().add(self.dedupestreamkey, streamobject)
        return dbresponse

    def __pstformat(self, record):
        formatedcreateddate = maya.parse(record['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        record['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        return record

    
    def __getdivisionname(self, divisions, divisionid):
        for division in divisions:
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

    

