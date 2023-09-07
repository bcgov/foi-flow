
from os import stat
from re import VERBOSE

from request_api.models.FOIUsers import FOIUser
from request_api.models.default_method_result import DefaultMethodResult
from request_api.models.OperatingTeams import OperatingTeam
from request_api.services.external.keycloakadminservice import KeycloakAdminService
import logging

class userservice:
    """ FOI user service

    """
    def syncusers(self):
        operatingteams = OperatingTeam().getalloperatingteams()
        for operatingteam in operatingteams:
            groupmembers = KeycloakAdminService().getmembersbygroupnameandtype(operatingteam['name'], operatingteam['type'])
            if groupmembers not in (None, '',[]) and len(groupmembers) > 0: 
                groupdata = groupmembers[0]
                if 'members' in groupdata and len(groupdata['members']) > 0:
                    kcusers = groupdata['members']
                    for user in kcusers:
                        self.__persistuser(user)       
            
        return DefaultMethodResult(True,'Users synced for foi-mod')
    
    def __persistuser(self, user):
        foiuser = FOIUser()            
        foiuser.username = user["origusername"] 
        foiuser.preferred_username = user["username"] 
        foiuser.firstname = user["firstname"] 
        foiuser.lastname = user["lastname"] 
        foiuser.email = user["email"] 
        foiuser.isactive = user["enabled"]
        return FOIUser().saveuser(foiuser)


    def getusers(self):
        return FOIUser().getall()

 
    