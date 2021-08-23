import requests
import os
import ast

class KeycloakAdminService:

    keycloakhost = os.getenv('KEYCLOAK_ADMIN_HOST')
    keycloakrealm = os.getenv('KEYCLOAK_ADMIN_REALM')
    keycloakclientid = os.getenv('KEYCLOAK_ADMIN_CLIENT_ID')
    keycloakclientsecret = os.getenv('KEYCLOAK_ADMIN_CLIENT_SECRET')
    keycloakadminserviceaccount = os.getenv('KEYCLOAK_ADMIN_SRVACCOUNT')
    keycloakadminservicepassword = os.getenv('KEYCLOAK_ADMIN_SRVPASSWORD')
    keycloakadminintakegroupid = os.getenv('KEYCLOAK_ADMIN_INTAKE_GROUPID')
    
        
    def get_token(self):
        
        url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(self.keycloakhost,self.keycloakrealm)        
        params = {

            'client_id': self.keycloakclientid,
            'grant_type': 'password',
            'username' : self.keycloakadminserviceaccount,
            'password': self.keycloakadminservicepassword,
            'client_secret':self.keycloakclientsecret
        }
        x = requests.post(url, params, verify=True).content.decode('utf-8')       
        return str(ast.literal_eval(x)['access_token'])        

    def getusers(self):
        return self.getGroupMembersById(self.keycloakadminintakegroupid)
    
    def getGroups(self, allowedGroups = None):
        url ='{0}/auth/admin/realms/{1}/groups'.format(self.keycloakhost,self.keycloakrealm)
        groupsResponse = requests.get(url, headers=self._getHeaders_())
        groups = []
        if groupsResponse.status_code == 200 and groupsResponse.content != '': 
            globalGroups =  groupsResponse.json()         
            for group in globalGroups:
                if allowedGroups is not None:
                    for allowedGroup in allowedGroups:
                        print(group["name"])
                        print(allowedGroup)
                        if group["name"] == allowedGroup:   
                            groups.append({'id': group['id'],'name':group['name']})
                else:
                    groups.append({'id': group['id'],'name':group['name']})
        return groups  
    
 
    def getGroupsAndMembers(self, allowedGroups = None):
        allowedGroups = self.getGroups(allowedGroups)
        print(allowedGroups)
        for group in allowedGroups:
            group["members"] = self.getGroupMembersById(group["id"])
        return allowedGroups  
    
    def getGroupMembersByName(self, groupName):
        groups = self.getGroups()
        for group in groups:
            if group["name"] == groupName:
                return self.getGroupMembersById(group["id"])

    def getGroupMembersById(self, groupId):
        groupUrl ='{0}/auth/admin/realms/{1}/groups/{2}/members'.format(self.keycloakhost,self.keycloakrealm,groupId)
        groupResponse = requests.get(groupUrl, headers=self._getHeaders_())
        users = []
        if groupResponse.status_code == 200 and groupResponse.content != '': 
            for user in groupResponse.json():                
                _user =  {
                       'id':user['id'],
                       'username':user['username'],                       
                       'email':user['email'],
                       'firstname':user['firstName'],
                       'lastname':user['lastName']                       
                   } 
                users.append(_user)

        return users 
        
    def _getHeaders_(self):
        return {
            "Authorization": "Bearer " + self.get_token(),
            "Content-Type": "application/json",
        }    