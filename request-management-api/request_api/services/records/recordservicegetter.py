
from os import stat, path,getenv
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
import json
from datetime import datetime
import maya
import uuid
import logging
import copy
from request_api.services.records.recordservicebase import recordservicebase 

class recordservicegetter(recordservicebase):
    """ This class consolidates retrival of FOI Records for actors: iao and ministry. 
    """

    def fetch(self, requestid, ministryrequestid):
        result = {'dedupedfiles': 0, 'convertedfiles': 0, 'removedfiles': 0}
        try:
            _ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
            divisions = FOIMinistryRequestDivision.getdivisions(ministryrequestid, _ministryversion)
            uploadedrecords = FOIRequestRecord.fetch(requestid, ministryrequestid)
            batchids = []
            resultrecords = []
            if len(uploadedrecords) > 0:
                computingresponses, err = self.makedocreviewerrequest('GET', '/api/dedupestatus/{0}'.format(ministryrequestid))
                if err is None: 
                    _convertedfiles, _dedupedfiles, _removedfiles = self.__getcomputingsummary(computingresponses)
                    for record in uploadedrecords:
                        _computingresponse = self.__getcomputingresponse(computingresponses, "recordid", record)
                        _record = self.__preparerecord(record,_computingresponse, computingresponses,divisions)
                        resultrecords.append(_record)
                        if record["batchid"] not in batchids:
                            batchids.append(record["batchid"])  
                    if computingresponses not in (None, []) and len(computingresponses) > 0:
                        resultrecords = self.__handleduplicate(resultrecords)  
                    result["convertedfiles"] =  _convertedfiles
                    result["dedupedfiles"] = _dedupedfiles
                    result["removedfiles"] =  _removedfiles 
            result['batchcount'] = len(batchids)
            result["records"] = resultrecords
        except Exception as exp:
            logging.info(exp)
        return result 

    def __preparerecord(self, record, _computingresponse, computingresponses, divisions):
        _record = self.__pstformat(record)
        if _computingresponse not in (None, []):
            documentmasterid = _computingresponse["documentmasterid"]
            _record['isduplicate'] = _computingresponse['isduplicate']
            _record['attributes'] = self.__formatrecordattributes(_computingresponse['attributes'], divisions)
            _record['isredactionready'] = _computingresponse['isredactionready']
            _record['trigger'] = _computingresponse['trigger']
            _record['documentmasterid'] = _computingresponse["documentmasterid"]
            _record['outputdocumentmasterid'] = documentmasterid 
            _computingresponse_err = self.__getcomputingerror(_computingresponse)
            if _computingresponse_err is not None:
                _record['failed'] = _computingresponse_err
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
                _computingresponse_err = self.__getcomputingerror(attachment)
                if _computingresponse_err is not None:
                    _attachement['failed'] = _computingresponse_err
                _record['attachments'].append(_attachement)                      
                            
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
            if self.isvalid("isduplicate",result) and result["isduplicate"] == True and self.isvalid("duplicatemasterid",result):
                _resultrecords = self.__mergeduplicatedivisions(resultrecords, result["duplicatemasterid"], self.__getrecorddivisions(result["attributes"]))
            if "attachments" in result:
                for attachment in result["attachments"]:
                    if self.isvalid("isduplicate",attachment) and attachment["isduplicate"] == True and self.isvalid("duplicatemasterid", attachment):
                        _resultrecords = self.__mergeduplicatedivisions(resultrecords, attachment["duplicatemasterid"], self.__getrecorddivisions(attachment["attributes"]))
        return _resultrecords              


    def __mergeduplicatedivisions(self, _resultrecords, duplicatemasterid, divisions):
        for entry in _resultrecords:
            if "documentmasterid" in entry and int(entry["documentmasterid"]) == int(duplicatemasterid):
                entattributes = entry["attributes"]
                entattributes["divisions"] = self.__mergedivisions(entattributes, divisions) 
                entry["attributes"] = entattributes
            if "attachments" in entry:
                for attachment in entry["attachments"]:
                    if "documentmasterid" in attachment and int(attachment["documentmasterid"]) == int(duplicatemasterid): 
                        attattributes = attachment["attributes"]
                        attattributes["divisions"] = self.__mergedivisions(attachment["attributes"], divisions)    
                        attachment["attributes"] = attattributes
        return _resultrecords
    
    def __getrecorddivisions(self, _attributes):
        if isinstance(_attributes, str):
            _attributes = json.loads(_attributes)  
        return _attributes.get('divisions', [])  
    
    def __mergedivisions(self, _attributes, divisions):
        srcdivisions = self.__getrecorddivisions(_attributes)
        merged = srcdivisions
        for entry in divisions:
            isduplicate = False
            for srcdivision in srcdivisions:
                if entry["divisionid"] == srcdivision["divisionid"]:
                    isduplicate = True
            if isduplicate == False:
                merged.append(entry)
        return merged

    def __getcomputingresponse(self, response, filterby, data: any):
        if filterby == "recordid":
            filtered_response = [x for x in response if x["recordid"] == data["recordid"] and x["filename"] == data["filename"]]
            return filtered_response[0] if len(filtered_response) > 0 else []
        elif filterby == "parentid":
            filtered_response = [x for x in response if x["isattachment"] == True]
            return self.__getattachments(filtered_response, [], data)
        else:
            logging.info("not matched")

    def __getattachments(self, response, result, data):
        filtered, result = self.__attachments2(response, result, data)
        for subentry in result:
            filtered, result = self.__attachments2(filtered, result, subentry["documentmasterid"])
        return result
    
    def __attachments2(self, response, result, data):
        filtered = []
        for entry in response:
            if entry["parentid"] not in [None, ""] and int(entry["parentid"]) == int(data):
                result.append(entry)
            else:
                filtered.append(entry)
        return filtered, result  

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
            if entry["conversionstatus"] != "completed" or entry["deduplicationstatus"] != "completed":
                _dedupedfiles += 1
        return _convertedfiles, _dedupedfiles, _removedfiles
    
    def __pstformat(self, record):
        if type(record["created_at"]) is str and "|" in record["created_at"]:
            return record
        formatedcreateddate = maya.parse(record['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        record['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        return record

    
    def __getdivisionname(self, divisions, divisionid):
        for division in divisions:
            if division['division.divisionid'] == divisionid:
                return division['division.name']
        return None
