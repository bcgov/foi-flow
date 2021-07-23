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
        
        url = '{0}auth/realms/{1}/protocol/openid-connect/token'.format(self.keycloakhost,self.keycloakrealm)
        params = {

            'client_id': self.keycloakclientid,
            'grant_type': 'password',
            'username' : self.keycloakadminserviceaccount,
            'password': self.keycloakadminservicepassword,
            'client_secret':self.keycloakclientsecret
        }
        x = requests.post(url, params, verify=True).content.decode('utf-8')       
        return ast.literal_eval(x)['access_token']        

    def getusers(self):

        token = self.get_token() ##TODO: IMPLEMENT TOKEN CACHING < 1000

        url ='{0}auth/admin/realms/{1}/groups/{2}/members'.format(self.keycloakhost,self.keycloakrealm,self.keycloakadminintakegroupid)
        headers = {
                'content-type': 'application/json',
                'Authorization' : 'Bearer '+ str(token)
                }
          
        x = requests.get(url, headers=headers)
        users = []
        if x.status_code == 200 and x.content != '':            
            for user in x.json():                
                _user =  {
                       'id':user['id'],
                       'username':user['username'],                       
                       'email':user['email'],
                       'firstname':user['firstName'],
                       'lastname':user['lastName']                       
                   } 
                users.append(_user)

        return users    