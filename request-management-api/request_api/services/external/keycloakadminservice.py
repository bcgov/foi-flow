import requests
import os
import ast
import request_api


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

   
    def getgroups(self, allowedgroups = None):
        groups = []
        globalgroups = self.getallgroups()         
        for group in globalgroups:
            if allowedgroups is not None:
                for allowedgroup in allowedgroups:
                    if self.formatgroupname(group["name"]) == self.formatgroupname(allowedgroup):   
                        groups.append({'id': group['id'],'name':group['name']})
            else:
                groups.append({'id': group['id'],'name':group['name']})
        return groups  
    
    
    def getallgroups(self):
        if request_api.cache.get("kcgroups") is not None:
            return request_api.cache.get("kcgroups")
        url ='{0}/auth/admin/realms/{1}/groups'.format(self.keycloakhost,self.keycloakrealm)
        groupsresponse = requests.get(url, headers=self.getheaders())
        groups = []
        if groupsresponse.status_code == 200 and groupsresponse.content != '': 
            globalgroups =  groupsresponse.json()         
            for group in globalgroups:
                groups.append({'id': group['id'],'name':group['name']})
        request_api.cache.set("kcgroups", groups, os.getenv('CACHE_TIMEOUT'))
        return groups      
    
 
    def getgroupsandmembers(self, allowedgroups = None):
        allowedgroups = self.getgroups(allowedgroups)
        for group in allowedgroups:
            group["members"] = self.getgroupmembersbyid(group["id"], group["name"])
        return allowedgroups  
    

    def getgroupmembersbyid(self, groupid, groupname):
        cachename=self.getcachename(groupname)
        if request_api.cache.get(cachename) is not None:
            return request_api.cache.get(cachename)
        groupurl ='{0}/auth/admin/realms/{1}/groups/{2}/members'.format(self.keycloakhost,self.keycloakrealm,groupid)
        groupresponse = requests.get(groupurl, headers=self.getheaders())
        users = []
        if groupresponse.status_code == 200 and groupresponse.content != '': 
            for user in groupresponse.json():           
                _user =  {
                       'id':user['id'],
                       'username':user['username'],                       
                       'email': user['email'] if 'email' in user is not None else None,
                       'firstname':user['firstName'] if 'firstName' in user is not None else None,
                       'lastname': user['lastName'] if 'lastName' in user is not None else None                        
                   } 
                users.append(_user)
        request_api.cache.set(cachename, users, os.getenv('CACHE_TIMEOUT'))
        return users 
        
    def getheaders(self):
        return {
            "Authorization": "Bearer " + self.get_token(),
            "Content-Type": "application/json",
        }  
    
    def formatgroupname(self,input):
        input = input.lower()
        input = input.replace(' ', '')
        return input  
        
    def getcachename(self,groupname):
        return "kc_"+groupname.replace(' ','').lower()+"_cache"
    