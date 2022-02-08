
from os import stat
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.utils.enums import UserGroup
from request_api.models.FOIAssignees import FOIAssignee

class assigneeservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def getgroupsandmembersbytypeandstatus(self, requesttype, status, bcgovcode=None):
        if requesttype is None and status is None:
           return KeycloakAdminService().getgroupsandmembers(self.__getgroupsbytype(requesttype, bcgovcode)) 
        else:
            if status is None:
                return self.getgroupsandmembersbytype(requesttype,bcgovcode)
            else:
                filteredgroups = self.__getgroups(requesttype, status, bcgovcode)
                if filteredgroups is not None:
                    return KeycloakAdminService().getgroupsandmembers(filteredgroups)
            return None
            
    def getmembersbygroupname(self, groupname):
        return KeycloakAdminService().getgroupsandmembers([groupname]) 
    
    def getgroupsandmembersbytype(self, requesttype,bcgovcode):  
        groups = []
        groupmappings = self.__getgroupmappings(requesttype,bcgovcode)
        groupmembers = KeycloakAdminService().getgroupsandmembers(self.__getgroups(requesttype, bcgovcode))   
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

    def __getgroups(self,requesttype, status=None, bcgovcode=None):
        if status is None:
            return self.__getgroupsbytype(requesttype, bcgovcode)
        else:
            for groupmapping in self.__getgroupmappings(requesttype, bcgovcode):
                if self.__formatinput(groupmapping.get("status")) == status: 
                    return groupmapping.get("groups")
                
             
    def __getgroupsbytype(self, requesttype=None, bcgovcode=None):
        groups = []
        for groupmapping in self.__getgroupmappings(requesttype, bcgovcode):
            for group in groupmapping["groups"]:
                    if group not in groups :
                        groups.append(group)
        return groups
            
    def __getgroupmappings(self, requesttype, bcgovcode=None):
        if requesttype is None:
            return self.__personalgroupmappings(bcgovcode) + self.__generalgroupmappings(bcgovcode)
        else:
            if requesttype == "personal":
                return self.__personalgroupmappings(bcgovcode)
            else:
                return self.__generalgroupmappings(bcgovcode)
   
    def __formatinput(self, input):
        return input.lower().replace(' ', '')
        
    def __generalgroupmappings(self, bcgovcode=None):  
        groups = []      
        allgroups = [{"status":"Unopened", "groups":[UserGroup.intake.value]},
                {"status":"Intake In Progress","groups":[UserGroup.intake.value]},
                {"status":"Open","groups":[UserGroup.intake.value,UserGroup.flex.value]},
                {"status":"Closed","groups":[UserGroup.intake.value,UserGroup.flex.value]},
                {"status":"Call For Records","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Fee Estimate","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Deduplication","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"On Hold","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Harms Assessment","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Records Review","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Consult","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Ministry Sign Off","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Response","groups":[UserGroup.intake.value,UserGroup.flex.value,UserGroup.ministry.value]},
                {"status":"Redirect","groups":[UserGroup.intake.value,UserGroup.flex.value]},
            ]
        
        for entry in allgroups:
            groups.append({"status": entry["status"], "groups": self.__formatgroups(entry["groups"], bcgovcode)})
        
        return groups
      
       
    def __personalgroupmappings(self, bcgovcode=None):        
        groups = []      
        allgroups =  [{"status":"Unopened", "groups":[UserGroup.intake.value]},
                {"status":"Intake In Progress","groups":[UserGroup.intake.value]},
                {"status":"Open","groups":[UserGroup.intake.value,UserGroup.processing.value]},
                {"status":"Closed","groups":[UserGroup.intake.value,UserGroup.processing.value]},
                {"status":"Call For Records","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Fee Estimate","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Deduplication","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"On Hold","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Harms Assessment","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Records Review","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Consult","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Ministry Sign Off","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Response","groups":[UserGroup.intake.value,UserGroup.processing.value,UserGroup.ministry.value]},
                {"status":"Redirect","groups":[UserGroup.intake.value,UserGroup.processing.value]},
            ]
        for entry in allgroups:
            groups.append({"status": entry["status"], "groups": self.__formatgroups(entry["groups"], bcgovcode)})
        
        return groups
        
    def __formatgroups(self, groups, bcgovcode):
        formattedgroups = []
        for group in groups:
            formattedgroup = group if group.find('@bcgovcode') == -1 else self.__getministrygroupname(group, bcgovcode)
            if formattedgroup is not None:
                formattedgroups.append(formattedgroup)    
        return formattedgroups
    
    def __getministrygroupname(self, group, bcgovcode):
        return group.replace('@bcgovcode', bcgovcode) if bcgovcode is not None else None
                  
    def saveassignee(self, username, firstname, middlename, lastname):
        # FOIAssignee
        newassignee = FOIAssignee()
        newassignee.username = username
        newassignee.firstname = firstname
        newassignee.middlename = middlename
        newassignee.lastname = lastname
        return FOIAssignee.saveassignee(newassignee)
    