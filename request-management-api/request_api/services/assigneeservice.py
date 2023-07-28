
from os import stat
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.utils.enums import UserGroup
from request_api.models.FOIAssignees import FOIAssignee
from request_api.models.OperatingTeams import OperatingTeam
from request_api.models.FOIRequestTeams import FOIRequestTeam

class assigneeservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def getgroupsandmembersbytypeandstatus(self, requesttype, status, bcgovcode=None):
        if requesttype is None and status is None:
               return KeycloakAdminService().getgroupsandmembers(OperatingTeam.getalloperatingteams()) 
        else:
            filteredgroups = self.__getgroups(requesttype, status, bcgovcode)
            if filteredgroups is not None:
                return KeycloakAdminService().getgroupsandmembers(filteredgroups)
            return None
            
    def getmembersbygroupname(self, groupname):
        return KeycloakAdminService().getmembersbygroupname(groupname) 
    
    def getprocessingteamsbyrequesttype(self,requesttype):
        return FOIRequestTeam.getprocessingteamsbytype(requesttype)
            
    def saveassignee(self, username, firstname, middlename, lastname):
        # FOIAssignee
        newassignee = FOIAssignee()
        newassignee.username = username
        newassignee.firstname = firstname
        newassignee.middlename = middlename
        newassignee.lastname = lastname
        return FOIAssignee.saveassignee(newassignee)
    
    def __getgroups(self,requesttype, status=None, bcgovcode=None):
        return FOIRequestTeam.getteamsbystatusandprogramarea(requesttype,status,bcgovcode)
                
