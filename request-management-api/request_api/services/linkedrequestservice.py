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
        
    def bulk_add_linkedrequest(self, linkedrequest_a, new_linkedrequests, requestid, foiministryrequestid, user):
        try:
            print("newlinkedrequests", new_linkedrequests)
            formatted_new_linkedrequests = [{linkedrequest["axisrequestid"]: linkedrequest["govcode"]} for linkedrequest in new_linkedrequests]
            print("formatted", formatted_new_linkedrequests)
            current_linkedrequests = self.__get_current_linkedrequests(requestid, foiministryrequestid)
            if self.__valid_update(current_linkedrequests, formatted_new_linkedrequests):
                if foiministryrequestid is not None:
                    FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(formatted_new_linkedrequests), user)
                else:
                    FOIRawRequest().update_linkedrequests(requestid, json.dumps(formatted_new_linkedrequests), user)
                # Create link between linkedrequest_a and all the requests in its associated linkedrequests array
                print("SAVE BULK PARENT COMPLETED", linkedrequest_a)
                self.__create_two_way_link(new_linkedrequests, linkedrequest_a, user)
                db.session.commit()
                print("LINK PROCESS COMPLETED")
            return DefaultMethodResult(True,'Linkedrequest data saved', linkedrequest_a, 201)
        except Exception as e:
            db.session.rollback()
            raise Exception("Error when saving linkedrequests", e) from e

    def __create_two_way_link(self, linkedrequests, new_linkedrequest, userid):
        foiministryrequest_ids = [linkedrequest["foiministryrequestid"] for linkedrequest in linkedrequests if "foiministryrequestid" in linkedrequest and linkedrequest["foiministryrequestid"] is not None]
        foirawrequest_ids = [linkedrequest["rawrequestid"] for linkedrequest in linkedrequests if "rawrequestid" in linkedrequest and linkedrequest["foiministryrequestid"] is None]
        new_linkedrequest_axisid = next(iter(new_linkedrequest))
        if len(foirawrequest_ids) > 0:
            FOIRawRequest().bulkupdate_linkedrequests(foirawrequest_ids, json.dumps(new_linkedrequest), new_linkedrequest_axisid, userid)
            print("FOIRAW REQUEST CHILD LINK COMPLETED", foirawrequest_ids)
        if len(foiministryrequest_ids) > 0:
            FOIMinistryRequest().bulkupdate_linkedrequests(foiministryrequest_ids, json.dumps(new_linkedrequest), new_linkedrequest_axisid, userid)
            print("FOIMINISTRY REQUEST CHILD LINK COMPLETED", foiministryrequest_ids)

    def remove_linkedrequest(self, linkedrequest_a, linkedrequest_b, user):
        try:
            foiministryrequestid = linkedrequest_a["foiministryrequestid"]
            rawrequestid = linkedrequest_a["rawrequestid"]
            current_linkedrequests = self.__get_current_linkedrequests(rawrequestid, foiministryrequestid)
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_b, current_linkedrequests)
            if self.__valid_update(current_linkedrequests, updated_linkedrequests):
                if foiministryrequestid is not None:
                    FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(updated_linkedrequests), user)
                else:
                    FOIRawRequest().update_linkedrequests(rawrequestid, json.dumps(updated_linkedrequests), user)
                # Delink linkedrequest_a from linkedrequest_b
                print("REMOVE PARENT COMPLETED", linkedrequest_a)
                self.__remove_two_way_link(linkedrequest_a, linkedrequest_b, user)
                db.session.commit()
                print("DELINK PROCESS COMPLETED")
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
            if self.__valid_update(current_linkedrequests, updated_linkedrequests):
                FOIMinistryRequest().update_linkedrequests(foiministryrequestid, json.dumps(updated_linkedrequests), user)
                print("CHILD DELINK FOIMINISTRY COMPLETED", linkedrequest_b)
        else:
            current_linkedrequests = self.__get_current_linkedrequests(rawrequestid, None)
            updated_linkedrequests = self.__update_linkedrequest_list(linkedrequest_a, current_linkedrequests)
            if self.__valid_update(current_linkedrequests, updated_linkedrequests):
                FOIRawRequest().update_linkedrequests(rawrequestid, json.dumps(updated_linkedrequests), user)
                print("CHILD DELINK FOIRAW COMPLETED", linkedrequest_b)

    def __update_linkedrequest_list(self, linkedrequest_toremove, linkedrequests):
        # Remove linkedrequest_b from linkedrequest_a's array of linkedrequests if linkedrequest_b's axisrequestid exists as a key in the array
        if linkedrequests is not None and len(linkedrequests) > 0:
            linkedrequest_toremove_axisid = linkedrequest_toremove["axisrequestid"]
            return [linkedrequest for linkedrequest in linkedrequests if linkedrequest_toremove_axisid not in linkedrequest]
        return []
    
    def __valid_update(self, current_linkedrequests, updated_linkedrequests):
        current_axisids = [axisid for linkedrequest in current_linkedrequests for axisid in linkedrequest.keys()]
        updated_axisids = [axisid for linkedrequest in updated_linkedrequests for axisid in linkedrequest.keys()]
        print("VALIDATE")
        print("CURR", current_axisids)
        print("UPD", updated_axisids)
        if sorted(current_axisids) == sorted(updated_axisids):
            return False
        return True
    
    def __get_current_linkedrequests(self, requestid, foiministryrequestid):
        if foiministryrequestid is not None:
            return FOIMinistryRequest().get_linkedrequests(foiministryrequestid)
        return FOIRawRequest().get_linkedrequests(requestid)