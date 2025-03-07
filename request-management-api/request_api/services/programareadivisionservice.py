from request_api.models.ProgramAreaDivisions import ProgramAreaDivision
from request_api.services.programareaservice import programareaservice
from request_api.services.recordservice import recordservice
from request_api.models.default_method_result import DefaultMethodResult


class programareadivisionservice:

    def getallprogramareadivisions(self):
        """ Returns all active program area divisions
        """
        divisions = ProgramAreaDivision.getallprogramareadivisons()
        return self.__prepareprogramareas(divisions)
    
    def getallprogramareadivisonsandsections(self):
        """ Returns all active program area divisions and sections
        """
        divisions = ProgramAreaDivision.getallprogramareadivisonsandsections()
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
        records = recordservice().get_all_records_by_divisionid(divisionid)
        childdivisions = ProgramAreaDivision.getchilddivisions(divisionid)
        if len(records) > 0 or len(childdivisions) > 0:
            return DefaultMethodResult(False,'Division is currently tagged to various records or sections and cannot be disabled', divisionid)
        return ProgramAreaDivision.disableprogramareadivision(divisionid,userid)
    
    def getchilddivisions(self, divisionid):
        """ Returns all child divisions/sections for a given divisionid
        """
        return ProgramAreaDivision.getchilddivisions(divisionid)
    
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
