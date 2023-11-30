import requests
import os
import ast
import request_api
from request_api.models.OperatingTeams import OperatingTeam
from request_api.exceptions import BusinessException, Error
import redis

class KeycloakAdminService:

    keycloakhost = os.getenv('KEYCLOAK_ADMIN_HOST')
    keycloakrealm = os.getenv('KEYCLOAK_ADMIN_REALM')
    keycloakclientid = os.getenv('KEYCLOAK_ADMIN_CLIENT_ID')
    keycloakclientsecret = os.getenv('KEYCLOAK_ADMIN_CLIENT_SECRET')
    keycloakadminserviceaccount = os.getenv('KEYCLOAK_ADMIN_SRVACCOUNT')
    keycloakadminservicepassword = os.getenv('KEYCLOAK_ADMIN_SRVPASSWORD')
    keycloakadminintakegroupid = os.getenv('KEYCLOAK_ADMIN_INTAKE_GROUPID')
    cache_redis_url = os.getenv('CACHE_REDISURL')
    kctokenexpiry = os.getenv('KC_SRC_ACC_TOKEN_EXPIRY',1800)
    
    #Constants
    PRIMARY_GROUP_EMAIL_INDEX = 0 #index of the email address in the group information array
        
    def get_token(self):
        _accesstoken=None
        try:
            cache_client = redis.from_url(self.cache_redis_url,decode_responses=True)
            _accesstoken = cache_client.get("foi:kcsrcacnttoken")       
            if _accesstoken is None:
                url = '{0}/auth/realms/{1}/protocol/openid-connect/token'.format(self.keycloakhost,self.keycloakrealm)        
                params = {

                    'client_id': self.keycloakclientid,
                    'grant_type': 'password',
                    'username' : self.keycloakadminserviceaccount,
                    'password': self.keycloakadminservicepassword,
                    'client_secret':self.keycloakclientsecret
                }
                x = requests.post(url, params, verify=True).content.decode('utf-8')
                _accesstoken = str(ast.literal_eval(x)['access_token'])                
                cache_client.set("foi:kcsrcacnttoken",_accesstoken,ex=int(self.kctokenexpiry))
        except BusinessException as exception:
            print("Error happened while accessing token on KeycloakAdminService {0}".format(exception.message))
        finally:
            cache_client = None    
        return _accesstoken       

   
    def getgroups(self, allowedgroups = None):
        groups = []
        globalgroups = self.getallgroups()         
        if allowedgroups is not None:
            for allowedgroup in allowedgroups:
                for group in globalgroups:
                    if self.formatgroupname(group["name"]) == self.formatgroupname(allowedgroup["name"]):   
                        groups.append({'id': group['id'],'name':group['name'], 'type': allowedgroup["type"] })
        else:
            groups = globalgroups
        return groups  
    
    
    def getallgroups(self):
        url ='{0}/auth/admin/realms/{1}/groups'.format(self.keycloakhost,self.keycloakrealm)
        groupsresponse = requests.get(url, headers=self.getheaders())
        groups = []
        if groupsresponse.status_code == 200 and groupsresponse.content != '': 
            globalgroups =  groupsresponse.json()         
            for group in globalgroups:
                groups.append({'id': group['id'],'name':group['name'], 'type':None})
        return groups      
    
    def getgroup(self, groupname, type=None):
        groups = []
        allgroups = self.getallgroups()
        for entry in allgroups:
            if entry["name"] == groupname:
                groups.append({'id': entry['id'],'name':entry['name'], 'type': type})         
        return groups
 
    def getgroupsandmembers(self, allowedgroups = None):
        allowedgroups = self.getgroups(allowedgroups)
        for group in allowedgroups:
            group["members"] = self.getgroupmembersbyid(group["id"])
        return allowedgroups  
    

    # INPUT: groupid (string) - intake group id from the keyclock request
    # OUTPUT - group information (Array of strings) e.g. [email address]
    # Description: This method will fetch the group information from the keycloak server
    # by passing the group id as part of the parameters. The group information contains 
    # the email address of the group.
    def getgroupinformation(self, groupid):
        if groupid is None or groupid == '':
            return None
        groupurl ='{0}/auth/admin/realms/{1}/groups/{2}'.format(self.keycloakhost,self.keycloakrealm,groupid)
        groupresponse = requests.get(groupurl, headers=self.getheaders())
        if groupresponse.status_code == 200 and groupresponse.content != '': 
            return groupresponse.json()
        return None

    # INPUT: groupname (string) - intake group name from the keyclock request
    # OUTPUT - group information (Array of strings) e.g. [email address] 
    # Description: This method first extracts the group id from the group name.
    # The group id is then passed as a parameter to the getgroupinformation method
    # to fetch the group information. The group information contains the email address 
    def getgroupdetails(self, groupname): 
        group = self.getallgroups()
        for entry in group:
            if entry["name"] == groupname:
                groupinfo = self.getgroupinformation(entry['id'])
                if groupinfo is not None:
                    return groupinfo
        return None

    # INPUT: groupname (string) - intake group name from the keyclock request
    # OUTPUT - group email address (string)
    # Description: This method calls the getgroupdetails method to fetch the group information.
    # The group information contains the email address of the group. If the group information
    # does not have the email address in attributes, then an empty string is returned. 
    def processgroupEmail(self, groupname):
        try:
            groupinfo = self.getgroupdetails(groupname)
            if groupinfo is not None:
                if "attributes" in groupinfo and "groupEmailAddress" in groupinfo["attributes"]:
                    return groupinfo["attributes"]["groupEmailAddress"][KeycloakAdminService.PRIMARY_GROUP_EMAIL_INDEX]
            return ''
        except KeyError:
            return ''

    def getgroupmembersbyid(self, groupid):
        groupurl ='{0}/auth/admin/realms/{1}/groups/{2}/members'.format(self.keycloakhost,self.keycloakrealm,groupid)
        groupresponse = requests.get(groupurl, headers=self.getheaders())
        users = []
        if groupresponse.status_code == 200 and groupresponse.content != '': 
            for user in groupresponse.json():           
                _user =  self.__createuser(user)
                users.append(_user)
        if users not in (None, []):
            return sorted(users, key=lambda k: str(k['lastname']), reverse = False)
        return users 
    
    def getallusercount(self):
        userurl ='{0}/auth/admin/realms/{1}/users/count'.format(self.keycloakhost,self.keycloakrealm)
        userresponse = requests.get(userurl, headers=self.getheaders())
        if userresponse.status_code == 200 and userresponse.content != '':
            return int(userresponse.content)
        return 100
   
    def getallusers(self):
        usercount = self.getallusercount()
        userurl ='{0}/auth/admin/realms/{1}/users?max={2}'.format(self.keycloakhost,self.keycloakrealm,usercount)
        userresponse = requests.get(userurl, headers=self.getheaders())
        users = []
        if userresponse.status_code == 200 and userresponse.content != '': 
            for user in userresponse.json():           
                _user =  self.__createuser(user)
                users.append(_user)
        if users not in (None, []):
            return sorted(users, key=lambda k: str(k['lastname']), reverse = False)
        return users     
    
    def __createuser(self, user):
        return {
                'id':user['id'],
                'username': self.__formatusername(user),                       
                'email': user['email'] if 'email' in user is not None else None,
                'firstname':user['firstName'] if 'firstName' in user is not None else None,
                'lastname': user['lastName'] if 'lastName' in user is not None else None ,
                'enabled': user['enabled'],         
                'origusername': user['username']             
            } 

    def __formatusername(self,user):
        if "attributes" in user and "idir_username" in user["attributes"]:
            _username = user["attributes"]["idir_username"][0].lower()
            return _username+"@idir" if _username.endswith("@idir") == False else _username
        return user['username']
        
    def getheaders(self):
        return {
            "Authorization": "Bearer " + self.get_token(),
            "Content-Type": "application/json",
        }  
    
    def formatgroupname(self,input):
        return input.lower().replace(' ', '')  

    def getmembersbygroupname(self, groupname):
        operatingteam =  OperatingTeam.getteam(groupname)
        if operatingteam is not None:
            return self.getmembersbygroupnameandtype(operatingteam['name'], operatingteam['type'])
        return []
    

    def getmembersbygroupnameandtype(self, groupname, type):
        allowedgroups = self.getgroup(groupname, type)
        for group in allowedgroups:
            group["members"] = self.getgroupmembersbyid(group["id"])
        return allowedgroups

        

    
    