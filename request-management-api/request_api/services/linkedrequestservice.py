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
            if foiministryrequestid is not None:
                result = FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(updated_linkedrequests), user)
            else:
                result = FOIRawRequest().update_linkedrequests(rawrequestid, json.dumps(updated_linkedrequests), user)
            print("FIRST TXN")
            # db.session.commit()
            finalresult = self.__remove_two_way_link(linkedrequest_a, linkedrequest_b, user)
            print("SECOND TXN")
            db.session.commit()
            return DefaultMethodResult(True,'Linkedrequest data updated', linkedrequest_a["axisrequestid"], 201)
        except Exception as e:
            db.session.rollback()
            raise Exception("Error when delinking removed linkedrequests", e) from e
        finally:
            db.session.close()

    def __remove_two_way_link(self, linkedrequest_a, linkedrequest_b, user):
        # Delink linkedrequest_a from linkedrequest_b
        print("parent", linkedrequest_a)
        print("child", linkedrequest_b)
        if "foiministryrequestid" in linkedrequest_b and linkedrequest_b["foiministryrequestid"] is not None:
            print("min two way")
            current_linkedrequests = FOIMinistryRequest().get_linkedrequests(linkedrequest_b["foiministryrequestid"])
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_a, current_linkedrequests)
            return FOIMinistryRequest().update_linkedrequests(linkedrequest_b["foiministryrequestid"], json.dumps(updated_linkedrequests), user)
        if "rawrequestid" in linkedrequest_b and linkedrequest_b["rawrequestid"] is not None:
            print("raw two way")
            current_linkedrequests = FOIRawRequest().get_linkedrequests(linkedrequest_b["rawrequestid"])
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_a, current_linkedrequests)
            return FOIRawRequest().update_linkedrequests(linkedrequest_b["rawrequestid"], json.dumps(updated_linkedrequests), user)

    def __update_linkedrequest_list(self, linkedrequest_toremove, linkedrequests):
        # Remove linkedrequest_b from linkedrequest_a's array of linkedrequests if linkedrequest_b's axisrequestid exists as a key in the array
        linkedrequest_toremove_axisid = linkedrequest_toremove["axisrequestid"]
        if len(linkedrequests) > 0:
            print("REMOVE")
            return [linkedrequest for linkedrequest in linkedrequests if linkedrequest_toremove_axisid not in linkedrequest]
        return linkedrequests