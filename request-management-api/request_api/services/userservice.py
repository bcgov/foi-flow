
from os import stat
from re import VERBOSE

from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.models.FOIUsers import FOIUser
from request_api.models.default_method_result import DefaultMethodResult

import json
from flask import current_app
class userservice:
    """ FOI user service

    """
    def syncusers(self):
        foiusers = FOIUser().getall()
        kcusers = KeycloakAdminService().getallusers()
        for user in kcusers:
            action, foiusers = self.__validateuser(foiusers, user)
            if action in ("INSERT", "UPDATE"):
                foiuser = FOIUser()            
                foiuser.username = user["origusername"] 
                foiuser.preferred_username = user["username"] 
                foiuser.firstname = user["firstname"] 
                foiuser.lastname = user["lastname"] 
                foiuser.email = user["email"] 
                foiuser.isactive = user["enabled"] 
                if action == "INSERT":
                    FOIUser().saveuser(foiuser)
                else:
                    FOIUser().updateeuser(foiuser)     
            
        return DefaultMethodResult(True,'Users synced for foi-mod')
    
    def __validateuser(self, foiusers, kcuser):
        action = "INSERT"
        for foiuser in foiusers.copy():
            if foiuser['username'] == kcuser["origusername"]:
                action = "NA"
                if foiuser['firstname'] != kcuser["firstname"] or foiuser['lastname'] != kcuser["lastname"] or foiuser['email'] != kcuser["email"] or foiuser['isactive'] != kcuser["enabled"]:
                    action = "UPDATE"
                foiusers.remove(foiuser)    
        return action, foiusers
    

    def getusers(self):
        return FOIUser().getall()

 
    