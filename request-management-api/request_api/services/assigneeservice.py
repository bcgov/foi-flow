
from os import stat
from request_api.services.external.keycloakadminservice import KeycloakAdminService
import json
class assigneeservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def getGroupsAndMembersByTypeAndStatus(self, requesttype, status, bcgovcode=None):
        if requesttype is None and status is None:
           return KeycloakAdminService().getgroupsandmembers(self.getgroupsbytype(requesttype, bcgovcode)) 
        else:
            if status is None:
                return self.getgroupsandmembersbytype(requesttype,bcgovcode)
            else:
                filteredgroups = self.getgroups(requesttype, status, bcgovcode)
                if filteredgroups is not None:
                    return KeycloakAdminService().getgroupsandmembers(filteredgroups)
            return None
            
    def getMembersByGroupName(self, groupname):
        return KeycloakAdminService().getgroupsandmembers([groupname]) 
    
    def getgroupsandmembersbytype(self, requesttype,bcgovcode):  
        groups = []
        groupmappings = self.getgroupmappings(requesttype,bcgovcode)
        groupmembers = KeycloakAdminService().getgroupsandmembers(self.getgroups(requesttype, bcgovcode))   
        for groupmapping in groupmappings:
            groupentry = {}
            groupentry["status"] = groupmapping["status"]
            groupentry["groups"] =[]
            for group in groupmapping["groups"]:
                for groupmember in groupmembers:
                    if group == groupmember["name"]:
                        groupentry["groups"].append(groupmember)
            groups.append(groupentry)    
        return groups    

    def getgroups(self,requesttype, status=None, bcgovcode=None):
        if status is None:
            return self.getgroupsbytype(requesttype, bcgovcode)
        else:
            for groupmapping in self.getgroupmappings(requesttype, bcgovcode):
                if self.formatinput(groupmapping.get("status")) == status: 
                    return groupmapping.get("groups")
                
             
    def getgroupsbytype(self, requesttype=None, bcgovcode=None):
        groups = []
        for groupmapping in self.getgroupmappings(requesttype, bcgovcode):
            for group in groupmapping["groups"]:
                    if group not in groups :
                        groups.append(group)
        return groups
            
    def getgroupmappings(self, requesttype, bcgovcode=None):
        if requesttype is None:
            return self.personalgroupmappings(bcgovcode) + self.generalgroupmappings(bcgovcode)
        else:
            if requesttype == "personal":
                return self.personalgroupmappings(bcgovcode)
            else:
                return self.generalgroupmappings(bcgovcode)
   
    def formatinput(self, input):
        input = input.lower()
        input = input.replace(' ', '')
        return input
        
    def generalgroupmappings(self, bcgovcode=None):  
        groups = []      
        allgroups = [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Flex Team"]},
                {"status":"Closed","groups":["Intake Team","Flex Team"]},
                {"status":"Call For Records","groups":["Intake Team","Flex Team","@bcgovcode Ministry Team"]},
                {"status":"Redirect","groups":["Intake Team","Flex Team"]},
            ]
        
        for entry in allgroups:
            groups.append({"status": entry["status"], "groups": self.formatgroups(entry["groups"], bcgovcode)})
        
        return groups
      
       
    def personalgroupmappings(self, bcgovcode=None):        
        groups = []      
        allgroups =  [{"status":"Unopened", "groups":["Intake Team"]},
                {"status":"Intake In Progress","groups":["Intake Team"]},
                {"status":"Open","groups":["Intake Team","Processing Team"]},
                {"status":"Closed","groups":["Intake Team","Flex Team"]},
                {"status":"Call For Records","groups":["Intake Team","Processing Team","@bcgovcode Ministry Team"]},
                {"status":"Redirect","groups":["Intake Team","Flex Team"]},
            ]
        for entry in allgroups:
            groups.append({"status": entry["status"], "groups": self.formatgroups(entry["groups"], bcgovcode)})
        
        return groups
        
    def formatgroups(self, groups, bcgovcode):
        formattedgroups = []
        for group in groups:
            formattedgroup = group if group.find('@bcgovcode') == -1 else self.getministrygroupname(group, bcgovcode)
            if formattedgroup is not None:
                formattedgroups.append(formattedgroup)    
        return formattedgroups
    
    def getministrygroupname(self, group, bcgovcode):
        return group.replace('@bcgovcode', bcgovcode) if bcgovcode is not None else None
                  