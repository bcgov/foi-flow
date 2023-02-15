import logging
import os
import requests
from request_api.utils.cache import clear_cache
from request_api.auth import AuthHelper

class cacheservice:
    
    def refreshcache(self):
        try:
            apiurl =  os.getenv("FOI_REQ_MANAGEMENT_API_URL")
            token = AuthHelper.getauthtoken()
            apiurls=[]
            result= False
            apiurls.append(apiurl+'/api/foiassignees')
            apiurls.append(apiurl+'/api/foiflow/programareas')
            apiurls.append(apiurl+'/api/foiflow/deliverymodes')
            apiurls.append(apiurl+'/api/foiflow/receivedmodes')
            apiurls.append(apiurl+'/api/foiflow/closereasons')
            apiurls.append(apiurl+'/api/foiflow/extensionreasons')
            apiurls.append(apiurl+'/api/foiflow/applicantcategories')
            apiurls.append(apiurl+'/api/foiflow/applicantcorrespondence/templates')
            resp_flag = clear_cache()
            if resp_flag:
                result=self.__invokeresources(apiurls,token)
            return result
        except Exception as ex:    
            logging.error(ex)        
        return False

    def __invokeresources(self, apiurls,token):
        try:
            for url in apiurls:
                requests.get(url, headers={'Authorization': token})
            return True
        except Exception as ex:    
            logging.error(ex)        
        return False
