from jinja2 import Template
from request_api.services.external.storageservice import storageservice
import json

class templatevaluebuilderservice:
    """This class is reserved for value builder service
    """
    
    
    def preparemetadata(self, data):        
        return {
            "to": data[""],
            "cc": data[""],
            "bcc": data[""],
            "subject": data[""],
            "body": data[""]            
        }
   
    def preparevalue(self, emailtemplatename, dynamictemplatevalues):        
        
        emailtemplatehtml= storageservice().download(emailtemplatename)
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')

        template = Template(emailtemplatehtml)
        dynamicvalues = dict(dynamictemplatevalues)
        templatedhtml = template.render(dynamicvalues)
        return templatedhtml
    

