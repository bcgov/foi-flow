from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.db import db
from request_api.utils.enums import StateName
import json
from dataclasses import dataclass

@dataclass
class DefaultMethodResult:
    def __init__(self, success, message, code=-1, data=None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data

class linkedrequestservice:
    def getlinkedrequestinfo(self, linkedrequests):
        linkedrequestinfo = FOIRawRequest.getlinkedrequestdetails(linkedrequests)
        return linkedrequestinfo

    def findrequestids(self, search_text, axisrequestid, ministrycode):
        raw_results = FOIRawRequest().getautofilllinkedrequestids(search_text, axisrequestid, ministrycode, 10)
        return raw_results
    
    def get_linkedfoiministryrequest_info_by_axisid(self, axisid):
        try:
            linkedrequestinfo = FOIMinistryRequest().get_linkedfoiministryrequest_info(axisid)
            linkedrequestinfo["requeststatus"] = StateName[linkedrequestinfo["requeststatus"]].value
            return linkedrequestinfo
        except Exception as e:
            raise Exception("Error when gathering additional foiministryrequest linked request info") from e
    
    def create_two_way_link(self, linkedrequests, new_linkedrequest, userid):
        try:
            foiministryrequest_ids = [linkedrequest["foiministryrequestid"] for linkedrequest in linkedrequests if "foiministryrequestid" in linkedrequest and linkedrequest["foiministryrequestid"] is not None] #axis ids from linked requests where indicaotr is TRUE
            foirawrequest_ids = [linkedrequest["rawrequestid"] for linkedrequest in linkedrequests if "rawrequestid" in linkedrequest and linkedrequest["foiministryrequestid"] is None] #axis ids from linked requests where indicaotr is FALSE
            FOIRawRequest().bulkupdate_linkedrequests(foirawrequest_ids, new_linkedrequest, userid)
            FOIMinistryRequest().bulkupdate_linkedrequests(foiministryrequest_ids, new_linkedrequest, userid)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception("Error when creating two-way link for newly added linked requests", e) from e
        finally:
            db.session.close()

    def remove_linkedrequest(self, linkedrequest_a, linkedrequest_b, updated_linkedrequests, user):
        try:
            foiministryrequestid = linkedrequest_a["foiministryrequestid"]
            rawrequestid = linkedrequest_a["rawrequestid"]
            current_linkedrequests = self.__get_current_linkedrequests(rawrequestid, foiministryrequestid)
            if self.__valid_udpate(current_linkedrequests, updated_linkedrequests):
                if foiministryrequestid is not None:
                    FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(updated_linkedrequests), user)
                else:
                    FOIRawRequest().update_linkedrequests(rawrequestid, json.dumps(updated_linkedrequests), user)
                # Delink linkedrequest_a from linkedrequest_b
                self.__remove_two_way_link(linkedrequest_a, linkedrequest_b, user)
                db.session.commit()
            else:
                db.session.close()
            return DefaultMethodResult(True,'Linkedrequest data updated', linkedrequest_a["axisrequestid"], 201)
        except Exception as e:
            db.session.rollback()
            raise Exception("Error when delinking removed linkedrequests", e) from e

    def __remove_two_way_link(self, linkedrequest_a, linkedrequest_b, user):
        foiministryrequestid = linkedrequest_b["foiministryrequestid"]
        rawrequestid = linkedrequest_b["rawrequestid"]
        if foiministryrequestid is not None:
            current_linkedrequests = self.__get_current_linkedrequests(None, foiministryrequestid)
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_a, current_linkedrequests)
            if self.__valid_udpate(current_linkedrequests, updated_linkedrequests):
                return FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(updated_linkedrequests), user)
        else:
            current_linkedrequests = self.__get_current_linkedrequests(rawrequestid, None)
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_a, current_linkedrequests)
            if self.__valid_udpate(current_linkedrequests, updated_linkedrequests):
                return FOIRawRequest().update_linkedrequests(rawrequestid, json.dumps(updated_linkedrequests), user)

    def __update_linkedrequest_list(self, linkedrequest_toremove, linkedrequests):
        # Remove linkedrequest_b from linkedrequest_a's array of linkedrequests if linkedrequest_b's axisrequestid exists as a key in the array
        linkedrequest_toremove_axisid = linkedrequest_toremove["axisrequestid"]
        return [linkedrequest for linkedrequest in linkedrequests if linkedrequest_toremove_axisid not in linkedrequest]
    
    def __valid_udpate(self, current_linkedrequests, updated_linkedrequests):
        return (current_linkedrequests is not None and len(current_linkedrequests) > 0) and (len(current_linkedrequests) != len(updated_linkedrequests))
    
    def __get_current_linkedrequests(self, requestid, foiministryrequestid):
        if foiministryrequestid is not None:
            return FOIMinistryRequest().get_linkedrequests(foiministryrequestid)
        return FOIRawRequest().get_linkedrequests(requestid)