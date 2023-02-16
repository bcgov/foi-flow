import logging
import os
import requests
from request_api.utils.cache import clear_cache
from request_api.auth import AuthHelper
from request_api.services.external.keycloakadminservice import KeycloakAdminService

class cacheservice:
    
    request_url = os.getenv("FOI_REQ_MANAGEMENT_API_URL")

    def refreshcache(self):
        try:
            result= False
            resp_flag = clear_cache()
            if resp_flag:
                apiurls = self.__getapilist()
                result=self.__invokeresources(apiurls)
            return result
        except Exception as ex:    
            logging.error(ex)        
        return False

    def __getapilist(self):
        try:
            apiurls=[]
            apiurls.append(self.request_url+'/api/foiassignees')
            apiurls.append(self.request_url+'/api/foiflow/programareas')
            apiurls.append(self.request_url+'/api/foiflow/deliverymodes')
            apiurls.append(self.request_url+'/api/foiflow/receivedmodes')
            apiurls.append(self.request_url+'/api/foiflow/closereasons')
            apiurls.append(self.request_url+'/api/foiflow/extensionreasons')
            apiurls.append(self.request_url+'/api/foiflow/applicantcategories')
            apiurls.append(self.request_url+'/api/foiflow/applicantcorrespondence/templates')
        except Exception as ex:    
            logging.error(ex)        
        return apiurls

    def __invokeresources(self, apiurls):
        try:
            
            headers= {"Authorization": "Bearer " + KeycloakAdminService().get_token()}
            for url in apiurls:
                requests.get(url, headers)
            return True
        except Exception as ex:    
            logging.error(ex)        
        return False
