
from re import T

from request_api.services.documentservice import documentservice
from request_api.services.workflowservice import workflowservice
from request_api.services.watcherservice import watcherservice
from request_api.services.commentservice import commentservice
from request_api.services.paymentservice import paymentservice
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator 
from request_api.services.foirequest.requestservicegetter import requestservicegetter 
from request_api.services.foirequest.requestservicecreate import requestservicecreate 
from request_api.services.foirequest.requestserviceupdate import requestserviceupdate
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.utils.enums import StateName
from request_api.services.commons.duecalculator import duecalculator
from request_api.utils.commons.datetimehandler import datetimehandler
import os
import json

class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI opened Request

    """
    
    def saverequest(self,foirequestschema, userid, foirequestid=None, ministryid=None, filenumber=None, version=None, rawrequestid=None, wfinstanceid=None):
        return requestservicecreate().saverequest(foirequestschema, userid, foirequestid, ministryid, filenumber, version, rawrequestid, wfinstanceid)     
    
    def saverequestversion(self,foirequestschema, foirequestid , ministryid, userid):
        responseschema = requestservicecreate().saverequestversion(foirequestschema, foirequestid , ministryid, userid) 
        if "paymentExpiryDate" in foirequestschema and foirequestschema["paymentExpiryDate"] not in (None, ""):
            paymentservice().createpayment(foirequestid, ministryid, foirequestschema, userid)
        return responseschema
            
    
    def saveministryrequestversion(self,ministryrequestschema, foirequestid , ministryid, userid, usertype = None):
         return requestservicecreate().saveministryrequestversion(ministryrequestschema, foirequestid , ministryid, userid, usertype)      
     
    def updaterequest(self,foirequestschema,foirequestid,userid):
        return requestserviceupdate().updaterequest(foirequestschema,foirequestid,userid) 

    def updateministryrequestduedate(self, ministryrequestid, duedate, userid):
        return requestserviceupdate().updateministryrequestduedate(ministryrequestid, duedate, userid)
    
    def postpaymentstatetransition(self, requestid, ministryrequestid, nextstatename, paymentdate):
        foirequest = self.getrequest(requestid, ministryrequestid)
        currentstatus = foirequest["stateTransition"][0]["status"] if "stateTransition" in foirequest and len(foirequest["stateTransition"])  > 1 else None
        status = FOIRequestStatus().getrequeststatusid(nextstatename)
        if currentstatus not in (None, "") and currentstatus == StateName.onhold.value:
            calc_duedate, calc_cfrduedate = self.calculateduedate(foirequest, paymentdate)
            foirequest['dueDate'] = calc_duedate
            foirequest['cfrDueDate'] = calc_cfrduedate
        foirequest['requeststatusid'] = status['requeststatusid']
        return self.saverequestversion(foirequest, requestid, ministryrequestid,'Online Payment')

    def getrequest(self,foirequestid,foiministryrequestid): 
        return requestservicegetter().getrequest(foirequestid, foiministryrequestid)
    
    def getrequestdetailsforministry(self,foirequestid, foiministryrequestid, authmembershipgroups):
        return requestservicegetter().getrequestdetailsforministry(foirequestid,foiministryrequestid, authmembershipgroups)
    
    def getrequestdetails(self,foirequestid, foiministryrequestid):
        return requestservicegetter().getrequestdetails(foirequestid, foiministryrequestid)
    
    def copywatchers(self, rawrequestid, ministries, userid):
        watchers = watcherservice().getrawrequestwatchers(int(rawrequestid))
        for ministry in ministries:           
            for watcher in watchers:
                watcherschema = {"ministryrequestid":ministry["id"],"watchedbygroup":watcher["watchedbygroup"],"watchedby":watcher["watchedby"],"isactive":True}
                watcherservice().createministryrequestwatcher(watcherschema, userid, None)
                
    def copycomments(self, rawrequestid, ministries, userid):
        comments = commentservice().getrawrequestcomments(int(rawrequestid))
        for ministry in ministries:           
            commentservice().copyrequestcomment(ministry["id"], comments, userid)
            
    def copydocuments(self, rawrequestid,ministries,userid):
        attachments = documentservice().getrequestdocuments(int(rawrequestid),"rawrequest")
        for ministry in ministries:
            documentservice().copyrequestdocuments(ministry["id"], attachments, userid)
    
    def postopeneventtoworkflow(self, id, requestschema, ministries):
        pid = workflowservice().syncwfinstance("rawrequest", requestschema['id'])
        workflowservice().postunopenedevent(id, pid, requestschema, "Open", ministries)            
    
    def postfeeeventtoworkflow(self, requestid, ministryrequestid, paymentstatus, nextstatename=None):
        foirequestschema = self.getrequestdetails(requestid, ministryrequestid)        
        workflowservice().postfeeevent(requestid, ministryrequestid, foirequestschema, paymentstatus, nextstatename)            
    
    def posteventtoworkflow(self, id, requestschema, data, usertype): 
        requeststatusid =  requestschema.get("requeststatusid") if 'requeststatusid' in requestschema  else None
        status = requestserviceconfigurator().getstatusname(requeststatusid) if requeststatusid is not None else None
        pid = workflowservice().syncwfinstance("ministryrequest", id)
        workflowservice().postopenedevent(id, pid, requestschema, data, status, usertype)
    
    def postcorrespondenceeventtoworkflow(self, requestid, ministryrequestid, applicantcorrespondenceid, attributes, templateid):
        foirequestschema = self.getrequestdetails(requestid, ministryrequestid)
        templatedetails = applicantcorrespondenceservice().gettemplatebyid(templateid)
        wfinstanceid = workflowservice().syncwfinstance("ministryrequest", ministryrequestid, True)
        workflowservice().postcorrenspodenceevent(wfinstanceid, ministryrequestid, foirequestschema, applicantcorrespondenceid, templatedetails.name, attributes)

    def calculateduedate(self, foirequest, paymentdate):
        duedate_includeoffhold, cfrduedate_includeoffhold = self.__isincludeoffhold()
        onhold_extend_days = duecalculator().getbusinessdaysbetween(foirequest["onholdTransitionDate"], paymentdate)
        isoffhold_businessday = duecalculator().isbusinessday(paymentdate)
        duedate_extend_days = onhold_extend_days + 1 if isoffhold_businessday == True and duedate_includeoffhold == True else onhold_extend_days
        cfrduedate_extend_days = onhold_extend_days + 1 if isoffhold_businessday == True and cfrduedate_includeoffhold == True else onhold_extend_days
        calc_duedate = duecalculator().addbusinessdays(foirequest["dueDate"], duedate_extend_days)    
        calc_cfrduedate = duecalculator().addbusinessdays(foirequest["cfrDueDate"], cfrduedate_extend_days) 
        return calc_duedate, calc_cfrduedate


    def __isincludeoffhold(self):
        payment_config_str = os.getenv("PAYMENT_CONFIG",'')        
        if payment_config_str in (None, ''):
            return True, True
        _paymentconfig = json.loads(payment_config_str)
        duedate_includeoffhold = True if _paymentconfig["duedate"]["includeoffhold"] == "Y" else False
        cfrduedate_includeoffhold = True if _paymentconfig["cfrduedate"]["includeoffhold"] == "Y" else False
        return duedate_includeoffhold, cfrduedate_includeoffhold

    