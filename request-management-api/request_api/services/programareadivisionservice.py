from request_api.models.ProgramAreaDivisions import ProgramAreaDivision

class programareadivisionservice:

    def getallprogramareadivisions(self):
        """ Returns all active program area divisions
        """
        divisions = ProgramAreaDivision.getallprogramareadivisons()
        return divisions
    
    def createprogramareadivision(self, data):
        """ Creates a program area division
        """
        return ProgramAreaDivision.createprogramareadivision(data)

    def updateprogramareadivision(self, divisionid, data):
        """ Updates an existing program area division
        """
        return ProgramAreaDivision.updateprogramareadivision(divisionid, data)
    
    def disableprogramareadivision(self, divisionid):
        """ Disable a program area division
        """
        return ProgramAreaDivision.disableprogramareadivision(divisionid)