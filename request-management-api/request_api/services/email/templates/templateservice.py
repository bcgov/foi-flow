from jinja2 import Template
from request_api.services.external.storageservice import storageservice
import json

class templateservice:
    """This class is reserved for jinja templating services integration.
    """
    
   
    def generatetemplate(self, emailtemplatename, dynamictemplatevalues):        
        
        emailtemplatehtml= storageservice().downloadtemplate(emailtemplatename)
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')
        
        template = Template(emailtemplatehtml)
        templatedhtml = template.render(dict(dynamictemplatevalues))
        return templatedhtml