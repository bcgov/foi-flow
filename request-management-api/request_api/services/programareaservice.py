from request_api.models.ProgramAreas import ProgramArea

class programareaservice:

    def getprogramareas(self):
        """ Returns the active records
        """
        return ProgramArea.getprogramareas()
    
    def getprogramareabyiaocode(self, iaocode):
        return ProgramArea.getprogramareabyiaocode(iaocode)

    def getprogramareasforministryuser(self, groups = None):
        """ Returns the active records
        """
        return ProgramArea.getprogramareasforministryuser(groups)
    
    def getprogramareabyprogramareaid(self, programareaid):
        return ProgramArea.getprogramareabyprogramareaid(programareaid)