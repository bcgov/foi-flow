import logging
import os
import requests
from request_api.utils.cache import clear_cache, clear_cache_key
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.utils.enums import CacheUrls
from request_api.exceptions import BusinessException

class cacheservice:
    
    request_url = os.getenv("FOI_REQ_MANAGEMENT_API_URL")

    def refreshcache(self, request_json):
        try:
            result= False
            if(request_json is not None and 'key' in request_json):
                result= self.__refreshcachebykey(request_json['key'])
            else:
                resp_flag = clear_cache()
                if resp_flag:
                    result=self.__invokeresources(self.__getapilistbykey())
            return result
        except Exception as ex:    
            logging.error(ex)   
        return False
    
    def __refreshcachebykey(self, key):
        try:
            result= False
            resp_flag = clear_cache_key(key)
            if resp_flag:
                result= self.__invokeresources(self.__getapilistbykey(key))
                return result
        except BusinessException as ex:    
            logging.error(ex)   
            return {'status': ex.status_code, 'message':ex.message}, 500     
        return False

    def __getapilistbykey(self, key=None):
        apiurls=[]
        if key is not None:
            apiurls.append(self.request_url+CacheUrls[key].value)
        else:
            apiurls.append(self.request_url+CacheUrls.keycloakusers.value)
            apiurls.append(self.request_url+CacheUrls.programareas.value)
            apiurls.append(self.request_url+CacheUrls.deliverymodes.value)
            apiurls.append(self.request_url+CacheUrls.receivedmodes.value)
            apiurls.append(self.request_url+CacheUrls.closereasons.value)
            apiurls.append(self.request_url+CacheUrls.extensionreasons.value)
            apiurls.append(self.request_url+CacheUrls.applicantcategories.value)
        return apiurls

    def __invokeresources(self, apiurls):
        try:
            headers= {"Authorization": "Bearer " + KeycloakAdminService().get_token()}
            for url in apiurls:
                requests.get(url, headers=headers)
            return True
        except BusinessException as ex:    
            logging.error(ex)   
            return {'status': ex.status_code, 'message':ex.message}, 500
