from jinja2 import Template
from request_api.services.external.storageservice import storageservice
from request_api.services.email.templates.templateconfig import templateconfig
from request_api.services.requestservice import requestservice
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice
from request_api.models.ApplicationCorrespondenceTemplates import ApplicationCorrespondenceTemplate
import json
import logging

class templateservice:
    """This class is reserved for jinja templating services integration.
    """
    
   
    def generate_by_servicename_and_id(self, servicename, requestid, ministryrequestid):
        try:
            _request = requestservice().getrequestdetails(requestid,ministryrequestid)
            requestjson = json.dumps(_request)
            return self.generate_by_servicename_and_schema(servicename, requestjson, ministryrequestid)
        except Exception as ex:
            logging.exception(ex)
        return None

    def generate_by_servicename_and_schema(self, servicename, requestjson, ministryrequestid, applicantcorrespondenceid = None):
        try:
            _template = self.__gettemplate(servicename)
            if _template is None:
                _templatename = self.__gettemplatenamewrapper(servicename, requestjson, ministryrequestid)
                _template = self.__gettemplate(_templatename)
            print("isnotreceipt ==== ", templateconfig().isnotreceipt(servicename))
            if (applicantcorrespondenceid and applicantcorrespondenceid != 0 and templateconfig().isnotreceipt(servicename)):
                emailtemplatehtml = self.__generatecorrespondencetetemplate(applicantcorrespondenceid)
            else:
                emailtemplatehtml= storageservice().downloadtemplate(_template.documenturipath)
            return self.__generatetemplate(requestjson, emailtemplatehtml, _template.description)
        except Exception as ex:
            logging.exception(ex)
        return None

    def __gettemplatenamewrapper(self, servicename, requestjson, ministryrequestid):
        _templatename = templateconfig().gettemplatename(servicename)
        if _templatename is None:
            _latesttemplatename = self.__getlatesttemplatename(ministryrequestid)
            if requestjson is not None and requestjson != {}:
                balancedue = float(requestjson['cfrfee']['feedata']["balanceDue"])
                prevstate = self.__getprevstate(requestjson)
                if balancedue > 0:
                    print("__gettemplatenamewrapper templatekey = HALFPAYMENT")
                    return "HALFPAYMENT"

                elif balancedue == 0:
                    templatekey = "FULLPAYMENT"
                    if prevstate.lower() == "response" or (_latesttemplatename and _latesttemplatename == 'PAYOUTSTANDING'):
                        templatekey = "PAYOUTSTANDINGFULLPAYMENT"
                    print("__gettemplatenamewrapper templatekey = ", templatekey)
                    return templatekey
        
        return _templatename
    
    def __getlatesttemplatename(self, ministryrequestid):
        latestcorrespondence = applicantcorrespondenceservice().getlatestapplicantcorrespondence(ministryrequestid)
        _latesttemplateid = latestcorrespondence['templateid'] if 'templateid' in latestcorrespondence else None
        if _latesttemplateid:
            return applicantcorrespondenceservice().gettemplatebyid(_latesttemplateid).name
        return None
    
    def __getprevstate(self, requestjson):
        return requestjson["stateTransition"][2]["status"] if "stateTransition" in requestjson and len(requestjson["stateTransition"])  > 3 else None

    def __gettemplate(self, templatename):
        return ApplicationCorrespondenceTemplate.get_template_by_name(templatename)
    
    def __generatetemplate(self, dynamictemplatevalues, emailtemplatehtml, title):
        headerfooterhtml = storageservice().downloadtemplate('/TEMPLATES/EMAILS/header_footer_template.html')
        if(emailtemplatehtml is None):
            raise ValueError('No template found')

        if(dynamictemplatevalues is None):
            raise ValueError('Values not found')
            
        if dynamictemplatevalues["assignedTo"] == None:
                dynamictemplatevalues["assignedToFirstName"] = ""
                dynamictemplatevalues["assignedToLastName"] = ""

        contenttemplate = Template(emailtemplatehtml)
        content = contenttemplate.render(dynamictemplatevalues)
        dynamictemplatevalues["content"] = content
        dynamictemplatevalues['title'] = title
        finaltemplate = Template(headerfooterhtml)
        finaltemplatedhtml = finaltemplate.render(dynamictemplatevalues)
        return finaltemplatedhtml, content

    
    def __generatecorrespondencetetemplate(self, applicantcorrespondenceid):
        return applicantcorrespondenceservice().getapplicantcorrespondencelogbyid(applicantcorrespondenceid)
