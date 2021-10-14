from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ProgramAreaDivisions import ProgramAreaDivision
from request_api.models.ProgramAreaDivisionStages import ProgramAreaDivisionStage
import json

class divisionstageservice:

    def getdivisionandstages(self, bcgovcode):
        divisionstages = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getdivisionstagesummary(programarea['programareaid'])
        for division in divisions:
            divisionid = division['count'] if division['count'] > 0 else 0
            divisionstages.append({"divisionid": division['divisionid'], "name": self.escapestr(division['name']), "stages": self.getstages(divisionid)})
        return divisionstages
    
    def getstages(self, divisionid):
        activestages = []
        division_stages = ProgramAreaDivisionStage.getprogramareadivisionstages(divisionid)
        for stage in division_stages:
            if stage['isactive'] == True:
                activestages.append({"stageid": stage['stageid'], "name": self.escapestr(stage['name'])})
        return activestages
    
    def escapestr(self,value):
        return value.replace(u"’", u"'")