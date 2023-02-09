from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ProgramAreaDivisions import ProgramAreaDivision
from request_api.models.ProgramAreaDivisionStages import ProgramAreaDivisionStage
import json

class divisionstageservice:

    def getdivisionandstages(self, bcgovcode):
        divisionstages = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getprogramareadivisions(programarea['programareaid'])
        divisions.sort(key=lambda item: (item['sortorder'], item['name']))        
        for division in divisions:
            divisionstages.append({"divisionid": division['divisionid'], "name": self.escapestr(division['name'])})
        return {"divisions": divisionstages, "stages": self.getstages()}
    
    def getstages(self):
        activestages = []
        division_stages = ProgramAreaDivisionStage.getprogramareadivisionstages()
        for stage in division_stages:
            if stage['isactive'] == True:
                activestages.append({"stageid": stage['stageid'], "name": self.escapestr(stage['name'])})
        return activestages
    
    def escapestr(self,value):
        return value.replace(u"’", u"'")