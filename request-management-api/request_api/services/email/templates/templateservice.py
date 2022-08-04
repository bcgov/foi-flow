from jinja2 import Template
from request_api.services.external.storageservice import storageservice
from request_api.services.email.templates.templateconfig import templateconfig
from request_api.services.requestservice import requestservice
import json
import logging

class templateservice:
    """This class is reserved for jinja templating services integration.
    """
    
   
    def generate_by_servicename_and_id(self, servicename, requestid, ministryrequestid):
        try:
            _request = requestservice().getrequestdetails(requestid,ministryrequestid)
            requestjson = json.dumps(_request)
            return self.generate_by_servicename_and_schema(servicename, requestjson)
        except Exception as ex:
            logging.exception(ex)
        return None

    def generate_by_servicename_and_schema(self, servicename, requestjson):
        try:
            _templatename = templateconfig().gettemplatename(servicename)
            return self.__generatetemplate(_templatename, requestjson)
        except Exception as ex:
            logging.exception(ex)
        return None
    
    def __generatetemplate(self, emailtemplatename, dynamictemplatevalues):  
        emailtemplatehtml= storageservice().downloadtemplate(emailtemplatename)
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')
        
        template = Template(emailtemplatehtml)
        templatedhtml = template.render(dynamictemplatevalues)
        return templatedhtml
