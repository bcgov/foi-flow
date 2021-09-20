
from os import stat
from request_api.services.external.keycloakadminservice import KeycloakAdminService
import json
class assigneeservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def getGroupsAndMembersByTypeAndStatus(self, requestType=None, status=None):
        if requestType is None and status is None:
           return KeycloakAdminService().getGroupsAndMembers(self._getGroupsByType()) 
        else:
            if status is None:
                return self.getGroupsAndMembersByType(requestType)
            else:
                filteredGroups = self._getGroups(requestType,status)
                if filteredGroups is not None:
                    return KeycloakAdminService().getGroupsAndMembers(filteredGroups)
            return None
            
    def getMembersByGroupName(self, groupName):
        for group in self._getGroupsByType():
             if self._formatInput(group) == groupName: 
                return KeycloakAdminService().getGroupsAndMembers([group])
        return None 
    
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

    def _getGroups(self,requestType=None,status=None):
        if status is None:
            return self._getGroupsByType(requestType)
        else:
            for groupMapping in self._getGroupMappings(requestType):
                if self._formatInput(groupMapping.get("status")) == status: 
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
   
    def _formatInput(self, input):
        input = input.lower()
        input = input.replace(' ', '')
        return input
        
    def generalGroupMappings(self):        
        return [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Flex Team"]},
                {"status":"Closed","groups":["Intake Team","Flex Team"]},
            ]
        
    def personalGroupMappings(self):        
        return [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Processing Team"]},
                {"status":"Closed","groups":["Intake Team","Flex Team"]},
            ]
                  