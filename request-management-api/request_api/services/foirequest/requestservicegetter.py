
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from dateutil.parser import parse


class requestservicegetter:
    """ This class consolidates retrival of FOI request for actors: iao and ministry. 
    """
       
    def getrequest(self,foirequestid,foiministryrequestid):        
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
        requestcontactinformation = FOIRequestContactInformation.getrequestcontactinformation(foirequestid,request['version'])
        requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(foirequestid,request['version'])
        requestministrydivisions = FOIMinistryRequestDivision.getdivisions(foiministryrequestid,requestministry['version'])
        
        baserequestinfo = self.__preparebaseinfo(request,foiministryrequestid,requestministry,requestministrydivisions)
        baserequestinfo['lastStatusUpdateDate'] = FOIMinistryRequest.getLastStatusUpdateDate(foiministryrequestid, requestministry['requeststatus.requeststatusid']).strftime(self.__genericdateformat()),
        for contactinfo in requestcontactinformation:
            if contactinfo['contacttype.name'] == 'Email':
                baserequestinfo.update({'email':contactinfo['contactinformation']})
            else:
                baserequestinfo.update({contactinfo['dataformat']:contactinfo['contactinformation']})

        additionalpersonalinfo ={}
        for applicant in requestapplicants:
            firstname = applicant['foirequestapplicant.firstname']
            middlename = applicant['foirequestapplicant.middlename']
            lastname = applicant['foirequestapplicant.lastname']
            businessname = applicant['foirequestapplicant.businessname']
            dobraw = applicant['foirequestapplicant.dob']
            dob = parse(dobraw).strftime(self.__genericdateformat()) if dobraw is not None else ''
            alsoknownas = applicant['foirequestapplicant.alsoknownas']
            requestortypeid = applicant['requestortype.requestortypeid']
            if requestortypeid == 1:
                baserequestinfo.update(self.__prepareapplicant(firstname, middlename, lastname, businessname))
            additionalpersonalinfo.update(self.__prepareadditionalpersonalinfo(requestortypeid, firstname, middlename, lastname, dob, alsoknownas))

        baserequestdetails, additionalpersonalinfodetails = self.preparepersonalattributes(foirequestid, request['version'])
        baserequestinfo.update(baserequestdetails)
        additionalpersonalinfo.update(additionalpersonalinfodetails)
        
        baserequestinfo['additionalPersonalInfo'] = additionalpersonalinfo
        originalduedate = FOIMinistryRequest.getrequestoriginalduedate(foiministryrequestid)       
        baserequestinfo['originalDueDate'] = originalduedate.strftime(self.__genericdateformat())
        return baserequestinfo
    
    def preparepersonalattributes(self, foirequestid, version):
        personalattributes = FOIRequestPersonalAttribute.getrequestpersonalattributes(foirequestid, version)
        baserequestdetails = {}
        additionalpersonalinfodetails = {}
                       
        for personalattribute in personalattributes:
            attribute, location = self.__preparepersonalattribute(personalattribute)
            if location == "main":
                baserequestdetails.update(attribute)
            elif location =="additionalPersonalInfo":
                additionalpersonalinfodetails.update(attribute)
        return baserequestdetails, additionalpersonalinfodetails

    def getrequestdetailsforministry(self,foirequestid,foiministryrequestid, authmembershipgroups):
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
        requestministrydivisions = FOIMinistryRequestDivision.getdivisions(foiministryrequestid,requestministry['version'])        
        
        baserequestinfo = {}
        if requestministry["assignedministrygroup"] in authmembershipgroups:
            baserequestinfo = self.__preparebaseinfo(request,foiministryrequestid,requestministry,requestministrydivisions)

        if request['requesttype'] == 'personal':
            requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(foirequestid,request['version'])
            additionalpersonalinfo ={}
            for applicant in requestapplicants:
                firstname = applicant['foirequestapplicant.firstname']
                middlename = applicant['foirequestapplicant.middlename']
                lastname = applicant['foirequestapplicant.lastname']
                dobraw = applicant['foirequestapplicant.dob']
                dob = parse(dobraw).strftime(self.__genericdateformat()) if dobraw is not None else ''
                requestortypeid = applicant['requestortype.requestortypeid']
                if requestortypeid == 1:
                    baserequestinfo.update(self.__prepareapplicant(firstname, middlename, lastname))
                additionalpersonalinfo.update(self.__prepareadditionalpersonalinfo(requestortypeid, firstname, middlename, lastname, dob))
            baserequestdetails, additionalpersonalinfodetails = self.preparepersonalattributes(foirequestid, request['version'])
            baserequestinfo.update(baserequestdetails)
            additionalpersonalinfo.update(additionalpersonalinfodetails)                
            baserequestinfo['additionalPersonalInfo'] = additionalpersonalinfo 
        return baserequestinfo

    def __preparebaseinfo(self,request,foiministryrequestid,requestministry,requestministrydivisions):
        _receiveddate = parse(request['receiveddate'])
        axissyncdatenoneorempty =  self.__noneorempty(requestministry["axissyncdate"]) 
        baserequestinfo = {
            'id': request['foirequestid'],
            'requestType': request['requesttype'],
            'receivedDate': _receiveddate.strftime('%Y %b, %d'),
            'receivedDateUF': parse(request['receiveddate']).strftime('%Y-%m-%d %H:%M:%S.%f'),
            'deliverymodeid':request['deliverymode.deliverymodeid'],
            'deliveryMode':request['deliverymode.name'],
            'receivedmodeid':request['receivedmode.receivedmodeid'],
            'receivedMode':request['receivedmode.name'],
            'assignedGroup': requestministry["assignedgroup"],
            'assignedTo': requestministry["assignedto"],
            'idNumber':requestministry["filenumber"],
            'axisRequestId': requestministry["axisrequestid"],
            'axisSyncDate': parse(requestministry["axissyncdate"]).strftime('%Y-%m-%d %H:%M:%S.%f') if axissyncdatenoneorempty == False else None,
            'requestPageCount': int(requestministry["requestpagecount"]) if requestministry["requestpagecount"] is not None else 0 ,
            'description': requestministry['description'],
            'fromDate': parse(requestministry['recordsearchfromdate']).strftime(self.__genericdateformat()) if requestministry['recordsearchfromdate'] is not None else '',
            'toDate': parse(requestministry['recordsearchtodate']).strftime(self.__genericdateformat()) if requestministry['recordsearchtodate'] is not None else '',
            'currentState':requestministry['requeststatus.name'],            
            'requeststatusid':requestministry['requeststatus.requeststatusid'],
            'requestProcessStart': parse(requestministry['startdate']).strftime(self.__genericdateformat()) if requestministry['startdate'] is not None else '',
            'dueDate':parse(requestministry['duedate']).strftime(self.__genericdateformat()),            
            'programareaid':requestministry['programarea.programareaid'],
            'category':request['applicantcategory.name'],
            'categoryid':request['applicantcategory.applicantcategoryid'],
            'assignedministrygroup':requestministry["assignedministrygroup"],
            'assignedministryperson':requestministry["assignedministryperson"],            
            'selectedMinistries':[{'code':requestministry['programarea.bcgovcode'],'id':requestministry['foiministryrequestid'],'name':requestministry['programarea.name'],'selected':'true'}],
            'divisions': self.getdivisions(requestministrydivisions),
            'onholdTransitionDate': self.getonholdtransition(foiministryrequestid),            
            'stateTransition': FOIMinistryRequest.getstatesummary(foiministryrequestid),
            'assignedToFirstName': requestministry["assignee.firstname"] if requestministry["assignedto"] != None else None,
            'assignedToLastName': requestministry["assignee.lastname"] if requestministry["assignedto"] != None else None,
            'assignedministrypersonFirstName': requestministry["ministryassignee.firstname"] if requestministry["assignedministryperson"] != None else None,
            'assignedministrypersonLastName': requestministry["ministryassignee.lastname"] if requestministry["assignedministryperson"] != None else None,
        }
        if requestministry['cfrduedate'] is not None:
            baserequestinfo.update({'cfrDueDate':parse(requestministry['cfrduedate']).strftime(self.__genericdateformat())})
        return baserequestinfo
    
    def getdivisions(self, ministrydivisions):
        divisions = []
        if ministrydivisions is not None:                      
            for ministrydivision in ministrydivisions:
                division = {
                    "foiministrydivisionid": ministrydivision["foiministrydivisionid"],
                    "divisionid": ministrydivision["division.divisionid"],
                    "divisionname": ministrydivision["division.name"],
                    "stageid": ministrydivision["stage.stageid"],
                    "stagename": ministrydivision["stage.name"],
                    "divisionDueDate": parse(ministrydivision['divisionduedate']).strftime(self.__genericdateformat()) if ministrydivision['divisionduedate'] is not None else None,
                    "eApproval": ministrydivision["eapproval"]
                    } 
                divisions.append(division) 
        return divisions

    
    def getonholdtransition(self, foiministryrequestid):
        onholddate = None
        transitions = FOIMinistryRequest.getrequeststatusById(foiministryrequestid)
        for entry in transitions:
            if entry['requeststatusid'] == 11:
                onholddate = parse(str(entry['created_at'])).strftime("%Y-%m-%d")
            else:
                if onholddate is not None:
                    break;
        return onholddate;
    
    def __genericdateformat(self):
        return '%Y-%m-%d'
    
    def __prepareapplicant(self,firstname= None, middlename= None, lastname= None, businessname= None):
        return {
                    'firstName': firstname,
                    'middleName': middlename,
                    'lastName': lastname,
                    'businessName': businessname,                                                
                }     
        
    def __prepareadditionalpersonalinfo(self, requestortypeid, firstname= None, middlename= None, lastname= None, dob= None, alsoknownas= None):
        if requestortypeid == 1:
            return {                            
                    'birthDate' : dob,
                    'alsoKnownAs': alsoknownas
            }
        elif requestortypeid == 2:
            return {
                    'anotherFirstName': firstname,
                    'anotherMiddleName': middlename,
                    'anotherLastName': lastname,                            
                    'anotherBirthDate' : dob,  
                    'anotherAlsoKnownAs': alsoknownas                      
                }                    
        elif requestortypeid == 3:
            return    {
                    'childFirstName': firstname,
                    'childMiddleName': middlename,
                    'childLastName': lastname,
                    'childAlsoKnownAs': alsoknownas,
                    'childBirthDate': dob,                      
                }                    
          
    def __preparepersonalattribute(self, personalattribute):
        if personalattribute['personalattributeid'] == 1:                   
            return {'publicServiceEmployeeNumber': personalattribute['attributevalue']}, "main"
        
        elif  personalattribute['personalattributeid'] == 2 :    
            return {'correctionalServiceNumber': personalattribute['attributevalue']}, "main"
        
        elif  personalattribute['personalattributeid'] == 3 :    
            return {'personalHealthNumber': personalattribute['attributevalue']}, "additionalPersonalInfo"
        
        elif personalattribute['personalattributeid'] == 4:     
            return {'adoptiveMotherFirstName': personalattribute['attributevalue']}, "main"
        
        elif personalattribute['personalattributeid'] == 5:     
            return {'adoptiveMotherLastName': personalattribute['attributevalue']}, "main"
        
        elif personalattribute['personalattributeid'] == 6:     
            return {'adoptiveFatherFirstName': personalattribute['attributevalue']}, "main"
        
        elif personalattribute['personalattributeid'] == 7:     
            return {'adoptiveFatherLastName': personalattribute['attributevalue']}, "main"         
          
    def __noneorempty(self, variable):
	    return True if not variable else False