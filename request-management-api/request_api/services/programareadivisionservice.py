from request_api.models.ProgramAreaDivisions import ProgramAreaDivision
from request_api.services.programareaservice import programareaservice
from request_api.services.recordservice import recordservice
import json
from request_api.models.default_method_result import DefaultMethodResult


class programareadivisionservice:

    def getallprogramareadivisions(self):
        """ Returns all active program area divisions
        """
        divisions = ProgramAreaDivision.getallprogramareadivisons()
        return self.__prepareprogramareas(divisions)
    
    def createprogramareadivision(self, data):
        """ Creates a program area division
        """
        return ProgramAreaDivision.createprogramareadivision(data)

    def updateprogramareadivision(self, divisionid, data,userid):
        """ Updates an existing program area division
        """
        return ProgramAreaDivision.updateprogramareadivision(divisionid, data,userid)
    
    def disableprogramareadivision(self, divisionid,userid):
        """ Disable a program area division
        """
        # Validation to see if division id exists in any records. If so deletion cannot be completed. 
        records = recordservice().get_all_records()
        for record in records:
            attributes = json.loads(record['attributes'])
            if any(int(divisionid) in division.values() for division in attributes["divisions"]):
                return DefaultMethodResult(False,'Division is currently tagged to various records and cannot be disabled at this time', divisionid)

        return ProgramAreaDivision.disableprogramareadivision(divisionid,userid)
    
    def __prepareprogramareas(self, data):
        """ Join program area name with division on programareaid
        """
        divisions = []
        areas = programareaservice().getprogramareas()
        for entry in data:
            area = next((a for a in areas if a["programareaid"] == entry["programareaid"]), None)
            if (area is not None):
                entry["programarea"] = area["name"]
                entry["areabcgovcode"] = area["bcgovcode"]
                entry["areaiaocode"] = area["iaocode"]
                divisions.append(entry)
        return divisions
