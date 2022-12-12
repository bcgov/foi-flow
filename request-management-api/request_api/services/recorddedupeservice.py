
from os import stat, path
from re import VERBOSE
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.external.eventqueueservice import eventqueueservice
from request_api.services.recordservice import recordservice
import json
from datetime import datetime
import maya

class recorddedupeservice:
    """ FOI record management service
    """
    
   
        
    def fetchmergedrecords(self, requestid, ministryrequestid):
        result= dict()
        print("ministryrequestid:",ministryrequestid)
        uploadedrecords= recordservice().fetch(requestid, ministryrequestid)
        #dedupedrecords = [{'documentid': 1, 'isduplicate': False}]
        dedupedrecords = [
            {
                "isduplicate": False,
                "documentid": 1,
                "version": 1,
                "filename": "test2.pdf",
                "filepath": "https://citz-foi-prod.objectstore.gov.bc.ca/edu-dev/ABC-345-345345/8ec4bb23-a642-40ec-910e-9cfcc21b067b.pdf",
                "foiministryrequestid": 1,
                "createdby": {
                "user": "dedupeservice"
                },
                "created_at": "2022-12-08T11:25:12.840930-08:00",
                "updatedby": "",
                "updated_at": "",
                "attributes": {
                "lastmodified": "2022-01-06T19:08:39.322Z",
                "divisions": [
                    {
                    "divisionid": 2
                    },
                    {
                    "divisionid": 37
                    }
                ],
                "batch": "9eb38c91-13c7-4ee1-aef7-a6b540a26bba"
                },
                "rank1hash": "0439f4e8d24def29ff6fbd65710b285da30ac439",
                "rank2hash": "",
                "pagecount": ""
            }
        ]
        for record in uploadedrecords:
            for dedupedrecord in dedupedrecords:
                if(dedupedrecord['documentid'] == record['recordid']):
                    record['isdeduplicated']= True
                    record['isduplicate']=dedupedrecord['isduplicate']
                else:
                    record['isdeduplicated']= False
                    record['isduplicate']=False
        result['records']= uploadedrecords
        result['dedupedfiles']= len(dedupedrecords)
        duplicaterecords = list(filter(lambda x: record['isduplicate'] == True, dedupedrecords))
        result['removedfiles']= len(duplicaterecords)
        return result

    
  


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



