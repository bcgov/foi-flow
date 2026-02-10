from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.utils.enums import StateName

class linkedrequestservice:

    def getlinkedrequestinfo(self, linkedrequests):
        linkedrequestinfo = FOIRawRequest.getlinkedrequestdetails(linkedrequests)
        return linkedrequestinfo

    def findrequestids(self, search_text, axisrequestid, ministrycode):
        print("searcj text", search_text)
        print("axisid", axisrequestid)
        raw_results = FOIRawRequest().getautofilllinkedrequestids(search_text, axisrequestid, ministrycode, 10)
        return raw_results
    
    def get_linkedfoiministryrequest_info_by_axisid(self, axisid):
        try:
            linkedrequestinfo = FOIMinistryRequest().get_linkedfoiministryrequest_info(axisid)
            print("GAHHHH", linkedrequestinfo)
            linkedrequestinfo["requeststatus"] = StateName[linkedrequestinfo["requeststatus"]].value
            print("FINAL", linkedrequestinfo)
            return linkedrequestinfo
        except Exception as e:
            raise Exception("Error when gathering additional foiministryrequest linked request info") from e
    