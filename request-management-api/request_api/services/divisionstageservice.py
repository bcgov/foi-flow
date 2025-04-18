from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ProgramAreaDivisions import ProgramAreaDivision
from request_api.models.ProgramAreaDivisionStages import ProgramAreaDivisionStage
import json

class divisionstageservice:

    def getdivisionandstages(self, bcgovcode):
        divisionstages = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getprogramareadivisions(programarea['programareaid'])
        divisions.sort(key=lambda item: (item["sortorder"] if item["sortorder"] is not None else float('inf'), item["name"]))      
        for division in divisions:
            divisionstages.append({"divisionid": division['divisionid'], "name": self.escapestr(division['name']),"sortorder": division['sortorder'],"issection":division['issection']})
        return {"divisions": divisionstages, "stages": self.getstages()}

    def getalldivisionsandsections(self, bcgovcode):
        divisionstages = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getallprogramareatags(programarea['programareaid'])
        divisions.sort(key=lambda item: (item["sortorder"] if item["sortorder"] is not None else float('inf'), item["name"]))        
        for division in divisions:
            divisionstages.append({"divisionid": division['divisionid'], "name": self.escapestr(division['name']),"sortorder": division['sortorder'],"issection":division['issection']})
        return {"divisions": divisionstages, "stages": self.getstages()}

    def getpersonalspecificdivisionandstages(self, bcgovcode):
        divisionstages = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getpersonalspecificprogramareadivisions(programarea['programareaid'])
        divisions.sort(key=lambda item: (item["sortorder"] if item["sortorder"] is not None else float('inf'), item["name"]))        
        for division in divisions:
            divisionstages.append({"divisionid": division['divisionid'], "name": self.escapestr(division['name']),"sortorder": division['sortorder'], "issection":division['issection']})
        return {"divisions": divisionstages, "stages": self.getstages()}

    def getpersonalspecificprogramareasections(self, bcgovcode):
        programareasections = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        _sections = ProgramAreaDivision.getpersonalrequestsprogramareasections(programarea['programareaid'])
        _sections.sort(key=lambda item: (item["sortorder"] if item["sortorder"] is not None else float('inf'), item["name"]))        
        for _section in _sections:
            programareasections.append({"divisionid": _section['divisionid'], "name": self.escapestr(_section['name']),"sortorder":_section['sortorder'],"issection":_section['issection']})
        return {"sections": programareasections}
    
    def getpersonalspecificdivisionsandsections(self, bcgovcode):
        programareasections = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        divisions = ProgramAreaDivision.getpersonalspecificprogramareadivisions(programarea['programareaid'])
        sections = ProgramAreaDivision.getpersonalrequestsdivisionsandsections(programarea['programareaid'])
        divisions.sort(key=lambda item: (item["sortorder"] if item["sortorder"] is not None else float('inf'), item["name"]))        
        for _division in divisions:
            divisionid = _division['divisionid']
            _sections = []                        
            for _section in sections:                
                if(_section['parentid'] == divisionid):
                    _sections.append(_section)
            programareasections.append({"divisionid": divisionid, "name": self.escapestr(_division['name']),"sortorder":_division['sortorder'],"issection":_division['issection'],"sections":_sections})
        return {"divisions": programareasections}

    def getpersonalspecificpeople(self, bcgovcode):
        people = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        _sections = ProgramAreaDivision.getpersonalrequestsprogramareapeople(programarea['programareaid'])
        for _section in _sections:
            people.append({"divisionid": _section['divisionid'], "name": self.escapestr(_section['name']), "sortorder":_section['sortorder'], "issection":_section['issection']})
        return {"people": people}

    def getpersonalspecificfiletypes(self, bcgovcode):
        filetypes = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        _sections = ProgramAreaDivision.getpersonalrequestsprogramareafiletypes(programarea['programareaid'])
        for _section in _sections:
            filetypes.append({"divisionid": _section['divisionid'], "name": self.escapestr(_section['name']), "sortorder":_section['sortorder'], "issection":_section['issection']})
        return {"filetypes": filetypes}

    def getpersonalspecificvolumes(self, bcgovcode):
        volumes = []
        programarea = ProgramArea.getprogramarea(bcgovcode)
        _sections = ProgramAreaDivision.getpersonalrequestsprogramareavolumes(programarea['programareaid'])
        for _section in _sections:
            volumes.append({"divisionid": _section['divisionid'], "name": self.escapestr(_section['name']), "sortorder":_section['sortorder'], "issection":_section['issection']})
        return {"volumes": volumes}

    def getstages(self):
        activestages = []
        division_stages = ProgramAreaDivisionStage.getprogramareadivisionstages()
        for stage in division_stages:
            if stage['isactive'] == True:
                activestages.append({"stageid": stage['stageid'], "name": self.escapestr(stage['name'])})
        return activestages
    
    def escapestr(self,value):
        return value.replace(u"’", u"'")