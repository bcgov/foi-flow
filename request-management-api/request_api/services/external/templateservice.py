from jinja2 import Template
from request_api.services.external.storageservice import storageservice
import json

class templateservice:
    """This class is reserved for jinja templating services integration.
    """
    
   
    def generatetemplate(self, dynamictemplatevalues):        
        
        print("Values::",dynamictemplatevalues)
        emailtemplatehtml= storageservice().prepares3urianddownload()
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')

        template = Template(emailtemplatehtml)
        dynamicvalues = dict(dynamictemplatevalues)
        print(dynamicvalues)
        templatedhtml = template.render(dynamicvalues)
        print("<<<>>>",templatedhtml)
        return templatedhtml
