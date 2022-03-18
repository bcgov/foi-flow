from request_api.models.ProgramAreas import ProgramArea

class programareaservice:

    def getprogramareas(self):
        """ Returns the active records
        """
        return ProgramArea.getprogramareas()