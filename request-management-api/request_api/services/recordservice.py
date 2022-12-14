
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
                # headers={'Authorization': token}
                headers={'Authorization': "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5NmxBaVpBUi0wTXAxNy1YaFlHSEZHLUZ5XzRzdTZuc2ZWWVE3YllyMGVFIn0.eyJleHAiOjE2NzA5NjkwMzIsImlhdCI6MTY3MDk2NTQzMiwiYXV0aF90aW1lIjoxNjcwOTY0ODAzLCJqdGkiOiI2MGU5ZTg4OC00YmIxLTQ5ZDAtOGNkNi1iZDFhZGJmM2U1ODAiLCJpc3MiOiJodHRwczovL2Rldi5vaWRjLmdvdi5iYy5jYS9hdXRoL3JlYWxtcy81azhkYmw0aCIsImF1ZCI6WyJjYW11bmRhLXJlc3QtYXBpIiwiZm9ybXMtZmxvdy13ZWIiLCJkb2N1bWVudC1yZWRhY3Rpb24tbWFwcGVyIiwicmVhbG0tbWFuYWdlbWVudCJdLCJzdWIiOiJmZjk4ZThmMS0wYWE2LTQyZWEtYWVlZS1mM2I4MmU4YWE0YjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJmb3Jtcy1mbG93LXdlYiIsIm5vbmNlIjoiZGJhMzBlNzQtMThhNy00NjkyLTg0MjctYTk3NWU0ZGIwZjdkIiwic2Vzc2lvbl9zdGF0ZSI6ImM3NmRmNjUwLTY2MTktNDlmNC1hY2NkLTczNGM5ZWUyYTFmYiIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDo0NDM5Mi8qIiwiaHR0cHM6Ly9kZXYtbWFyc2hhbC1mb2lyZXF1ZXN0LmFwcHMuc2lsdmVyLmRldm9wcy5nb3YuYmMuY2EiLCJodHRwczovL2Rldi5mb2lyZXF1ZXN0cy5nb3YuYmMuY2EiLCJodHRwOi8vMTI3LjAuMC4xOjMwMDAvKiIsImh0dHBzOi8vbG9jYWxob3N0OjQ0MzkyLyoiLCJodHRwczovL2Rldi1mb2lyZXF1ZXN0LmFwcHMuc2lsdmVyLmRldm9wcy5nb3YuYmMuY2EvKiIsIioiLCJodHRwczovL2Rldi1tYXJzaGFsLWZvaS1mZmEtcmVxdWVzdC5hcHBzLnNpbHZlci5kZXZvcHMuZ292LmJjLmNhLyoiLCJodHRwOi8vbG9jYWxob3N0OjE1MDAwLyoiLCJodHRwOi8vbG9jYWxob3N0OjMwMDAiLCJodHRwOi8vbG9jYWxob3N0OjQwMDAvKiIsImh0dHBzOi8vZmxvd2F4aXNhcGlkZXYuZ292LmJjLmNhLyoiLCJodHRwczovL2ZvaS1mbG93LXJlcG9ydGluZy1jODRiOTUtZGV2LmFwcHMuc2lsdmVyLmRldm9wcy5nb3YuYmMuY2Evc2FtbC9jYWxsYmFjaz9vcmdfc2x1Zz1kZWZhdWx0IiwiaHR0cHM6Ly9kZXYtZm9pLWZmYS1yZXF1ZXN0LmFwcHMuc2lsdmVyLmRldm9wcy5nb3YuYmMuY2EvKiIsImh0dHA6Ly8xMjcuMC4wLjE6MTUwMDAvKiIsImh0dHA6Ly9sb2NhbGhvc3Q6NTAwMC8qIiwiaHR0cDovL2ZvaWZsb3cubG9jYWw6MzAwMC8qIl0sInJlc291cmNlX2FjY2VzcyI6eyJyZWFsbS1tYW5hZ2VtZW50Ijp7InJvbGVzIjpbInZpZXctcmVhbG0iLCJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsIm1hbmFnZS1pZGVudGl0eS1wcm92aWRlcnMiLCJpbXBlcnNvbmF0aW9uIiwicmVhbG0tYWRtaW4iLCJjcmVhdGUtY2xpZW50IiwibWFuYWdlLXVzZXJzIiwicXVlcnktcmVhbG1zIiwidmlldy1hdXRob3JpemF0aW9uIiwicXVlcnktY2xpZW50cyIsInF1ZXJ5LXVzZXJzIiwibWFuYWdlLWV2ZW50cyIsIm1hbmFnZS1yZWFsbSIsInZpZXctZXZlbnRzIiwidmlldy11c2VycyIsInZpZXctY2xpZW50cyIsIm1hbmFnZS1hdXRob3JpemF0aW9uIiwibWFuYWdlLWNsaWVudHMiLCJxdWVyeS1ncm91cHMiXX0sImZvcm1zLWZsb3ctd2ViIjp7InJvbGVzIjpbImZvcm1zZmxvdy1jbGllbnQiLCJmb3Jtc2Zsb3ctcmV2aWV3ZXIiLCJmb3Jtc2Zsb3ctZGVzaWduZXIiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGNhbXVuZGEtcmVzdC1hcGkgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInJvbGUiOlsiZm9ybXNmbG93LWNsaWVudCIsImZvcm1zZmxvdy1yZXZpZXdlciIsImZvcm1zZmxvdy1kZXNpZ25lciJdLCJuYW1lIjoiTmljaG9sYXMgS2FuIiwiZ3JvdXBzIjpbIi9jYW11bmRhLWFkbWluIiwiL0ZsZXggVGVhbSIsIi9mb3Jtc2Zsb3cvZm9ybXNmbG93LWNsaWVudCIsIi9mb3Jtc2Zsb3cvZm9ybXNmbG93LWRlc2lnbmVyIiwiL2Zvcm1zZmxvdy9mb3Jtc2Zsb3ctcmV2aWV3ZXIiLCIvUmVhbG0gQWRtaW5pc3RyYXRvciJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJuaWNoa2FuQGlkaXIiLCJnaXZlbl9uYW1lIjoiTmljaG9sYXMiLCJmYW1pbHlfbmFtZSI6IkthbiIsImVtYWlsIjoibmljaG9sYXMua2FuQGdvdi5iYy5jYSJ9.e2PHv7XP_DLwS2_hrJakK8H3vueEKiRofXQQ6uQSAWLet0s6J8tnG-7lqzeutP_eztQbRXuBItI57gBn7VNoGRrTVsYXnn1lJVDs9mU-craUFdzS2veWvYYdHhAAa0hc1MqlmLmK3KW4cEnPqxRsTKsCK_SbUXNmya1UxkUN4HCoAAw9OI_j3X-ai3puy0BVUWRtLQQ6kdhCCOgknpkBEkimFjsmGb2MP6D1-7GJ4tCpMJtbjrZb7cD_ITGiJpdGxMFBPBPilMPoeSabpFii9ZcYEaxY6eoE5oPw3usdDmHexynfsjLArxAwCgiF15ugqTVAFWdeoRzgr2Fo2iNKTA"}
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
        result['records'] = self.__format(list(uploadedrecords.values()), divisions)
        result['dedupedfiles'] = len(dedupedrecords)
        result['batchcount'] = len(set(map(lambda record: record['attributes']['batch'], result['records'])))
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



