
from re import T

from request_api.services.documentservice import documentservice
from request_api.services.workflowservice import workflowservice
from request_api.services.watcherservice import watcherservice
from request_api.services.commentservice import commentservice
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator 
from request_api.services.foirequest.requestservicegetter import requestservicegetter 
from request_api.services.foirequest.requestservicecreate import requestservicecreate 
from request_api.services.foirequest.requestserviceupdate import requestserviceupdate 

class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI opened Request

    """
    
    def saverequest(self,foirequestschema, userid, foirequestid=None, ministryid=None, filenumber=None, version=None, rawrequestid=None, wfinstanceid=None):
        return requestservicecreate().saverequest(foirequestschema, userid, foirequestid, ministryid, filenumber, version, rawrequestid, wfinstanceid)     
    
    def saverequestversion(self,foirequestschema, foirequestid , ministryid, userid):
        return requestservicecreate().saverequestversion(foirequestschema, foirequestid , ministryid, userid)     
    
    def saveministryrequestversion(self,ministryrequestschema, foirequestid , ministryid, userid):
         return requestservicecreate().saveministryrequestversion(ministryrequestschema, foirequestid , ministryid, userid)      
     
    def updaterequest(self,foirequestschema,foirequestid,userid):
        return requestserviceupdate().updaterequest(foirequestschema,foirequestid,userid) 
        
    def getrequest(self,foirequestid,foiministryrequestid):  
        return requestservicegetter().getrequest(foirequestid, foiministryrequestid)
    
    def getrequestdetailsforministry(self,foirequestid, foiministryrequestid, authmembershipgroups):
        return requestservicegetter().getrequestdetailsforministry(foirequestid,foiministryrequestid, authmembershipgroups)
    
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
    
    def postopeneventtoworkflow(self, id, wfinstanceid, requestschema, ministries):        
        workflowservice().postunopenedevent(id, wfinstanceid, requestschema, "Open", ministries)            
            
    def posteventtoworkflow(self, id, wfinstanceid, requestschema, data, usertype): 
        requeststatusid =  requestschema.get("requeststatusid") if 'requeststatusid' in requestschema  else None 
        if requeststatusid is not None:
            status = requestserviceconfigurator().getstatusname(requeststatusid)
            workflowservice().postopenedevent(id, wfinstanceid, requestschema, data, status, usertype)