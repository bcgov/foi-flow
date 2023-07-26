[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Lifecycle:Experimental](https://img.shields.io/badge/Lifecycle-Experimental-339999)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

## foi-flow
Freedom of Information modernization. 

## Features

## Usage

## Requirements

## Installation

### For mac
#### Run the microservices in docker
1. Clone this repo
2. Place the appropriate .env file to the root folder of entire repo
3. Change docker-compose.yml line 152 from windows.Dockerfile to mac.Dockerfile
4. Make sure you are logged into the VPN if working remotely
5. Compose up the docker-compose.yml file in the root folder by either right-clicking and selecting 'Compose up' in VS Code or running the command 
```docker compose -f "docker-compose.yml" up -d --build```

#### Add IP address to hosts on local system if accessing remotely
1. Log into vpn
2. Click statistics icon (bottom left of AnyConnect, the graph icon)
3. Note down client address (IPv4)
4. In your terminal run the command ``` sudo nano /etc/hosts ```
5. Add the ip address from above to the list, with alias value ``` foiflow.local ```
6. Save and exit

#### API performance issues
The app (particularly the API) may run very slowly. Performance can be improved by turning off Redis caching, commenting out the following code in [KeycloakAdminService](https://github.com/bcgov/foi-flow/blob/main/request-management-api/request_api/services/external/keycloakadminservice.py) (at ```foi-flow/request-management-api/request_api/services/external/keycloakadminservice.py```). Make sure that you don't commit these changes. 

Comment out the following, and change the _accesstoken value to None
```diff
    def get_token(self):
        _accesstoken=None
        try:
+            #cache_client = redis.from_url(self.cache_redis_url,decode_responses=True)
-            cache_client = redis.from_url(self.cache_redis_url,decode_responses=True)
+            _accesstoken = None 
-            _accesstoken = cache_client.get("foi:kcsrcacnttoken")            
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
+                #cache_client.set("foi:kcsrcacnttoken",_accesstoken,ex=int(self.kctokenexpiry))
-                cache_client.set("foi:kcsrcacnttoken",_accesstoken,ex=int(self.kctokenexpiry))
        except BusinessException as exception:
            print("Error happened while accessing token on KeycloakAdminService {0}".format(exception.message))
+        #finally:
+            #cache_client = None
-        finally:
-            cache_client = None
        return _accesstoken      
```
Again, make sure you don't commit these changes.

## Project Status
The project is in the very early stages of development. The codebase will be changing frequently.

## Goals/Roadmap

## Getting Help or Reporting an Issue
To report bugs/issues/feature requests, please file an [issue.](https://github.com/bcgov/foi-flow/issues)

## How to Contribute

If you would like to contribute, please see our [contributing](CONTRIBUTING.md)
guidelines. Please note that this project is released with a
[Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this
project you agree to abide by its terms.

## License

    Copyright 2021 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy
    of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
