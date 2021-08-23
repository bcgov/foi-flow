
from os import stat
from request_api.services.external.keycloakadminservice import KeycloakAdminService
import json
class assigneeservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def getGroupsAndMembersByTypeAndStatus(self, requestType, status):  
        if status is None:
            return self.getGroupsAndMembersByType(requestType)
        else:
            return KeycloakAdminService().getGroupsAndMembers(self._getGroups(requestType,status))
    
    def getGroupsAndMembersByType(self, requestType):  
        groups = []
        groupMappings = self._getGroupMappings(requestType)
        groupMembers = KeycloakAdminService().getGroupsAndMembers(self._getGroups(requestType))   
        for groupMapping in groupMappings:
            groupEntry = {}
            groupEntry["status"] = groupMapping["status"]
            groupEntry["groups"] =[]
            for group in groupMapping["groups"]:
                for groupMember in groupMembers:
                    if group == groupMember["name"]:
                        groupEntry["groups"].append(groupMember)
            groups.append(groupEntry)    
        return groups    

    def _getGroups(self,requestType,status=None):
        if status is None:
            return self._getGroupsByType(requestType)
        else:
            for groupMapping in self._getGroupMappings(requestType):
                if self._formatstatus(groupMapping.get("status")) == status: 
                    return groupMapping.get("groups")
                        
    def _getGroupsByType(self,requestType=None):
        groups = []
        for groupMapping in self._getGroupMappings():
            for group in groupMapping["groups"]:
                    if group not in groups :
                        groups.append(group)
        return groups
            
    def _getGroupMappings(self, requestType=None):
        if requestType is None:
            return self.generalGroupMappings() + self.personalGroupMappings()
        else:
            if requestType == "personal":
                return self.personalGroupMappings()
            if requestType == "general":
                return self.generalGroupMappings()
   
    def _formatstatus(self, status):
        status = status.lower()
        status = status.replace(' ', '')
        return status
        
    def generalGroupMappings(self):        
        return [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Flex Team"]},
            ]
        
    def personalGroupMappings(self):        
        return [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Processing Team"]},
            ]
                  