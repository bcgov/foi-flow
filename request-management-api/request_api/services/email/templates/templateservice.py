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
            _templatename = self.__gettemplatenamewrapper(servicename, requestjson)
            return self.__generatetemplate(_templatename, requestjson)
        except Exception as ex:
            logging.exception(ex)
        return None

    def __gettemplatenamewrapper(self, servicename, requestjson):
        _templatename = templateconfig().gettemplatename(servicename)
        if _templatename is None:
            if requestjson is not None and requestjson != {}:
                balancedue = requestjson["cfrfee"]['feedata']['totalamountdue'] - requestjson["cfrfee"]['feedata']['amountpaid']
                if balancedue > 0:
                    return templateconfig().gettemplatename("HALFPAYMENT")
                elif balancedue == 0:
                    return templateconfig().gettemplatename("FULLPAYMENT")
                else: 
                    return None
        return _templatename
    
    def __generatetemplate(self, emailtemplatename, dynamictemplatevalues):  
        emailtemplatehtml= storageservice().downloadtemplate(emailtemplatename)
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')
            
        if dynamictemplatevalues["assignedTo"] == None:
                dynamictemplatevalues["assignedToFirstName"] = ""
                dynamictemplatevalues["assignedToLastName"] = ""

        template = Template(emailtemplatehtml)
        templatedhtml = template.render(dynamictemplatevalues)
        return templatedhtml
