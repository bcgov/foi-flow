
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from request_api.models.FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from dateutil.parser import parse
from request_api.services.cfrfeeservice import cfrfeeservice
from request_api.services.paymentservice import paymentservice
from request_api.services.subjectcodeservice import subjectcodeservice
from request_api.services.programareaservice import programareaservice
from request_api.utils.commons.datetimehandler import datetimehandler
from request_api.services.external.keycloakadminservice import KeycloakAdminService

class requestservicegetter:
    """ This class consolidates retrival of FOI request for actors: iao and ministry. 
    """
       
    def getrequest(self,foirequestid,foiministryrequestid):        
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
        requestcontactinformation = FOIRequestContactInformation.getrequestcontactinformation(foirequestid,request['version'])
        requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(foirequestid,request['version'])
        requestministrydivisions = FOIMinistryRequestDivision.getdivisions(foiministryrequestid,requestministry['version'])
        iaorestrictrequestdetails = FOIRestrictedMinistryRequest.getrestricteddetails(ministryrequestid=foiministryrequestid,type='iao')

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
        originalLdd= FOIMinistryRequest.getrequestoriginalduedate(foiministryrequestid).strftime(self.__genericdateformat())
        baserequestinfo['originalDueDate'] = parse(requestministry['originalldd']).strftime(self.__genericdateformat()) if requestministry['originalldd'] is not None else originalLdd
        baserequestinfo['iaorestricteddetails'] = iaorestrictrequestdetails
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
        ministryrestrictrequestdetails = FOIRestrictedMinistryRequest.getrestricteddetails(foiministryrequestid,type='ministry')
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
        baserequestinfo['ministryrestricteddetails'] = ministryrestrictrequestdetails
        return baserequestinfo
    
    def getrequestdetails(self,foirequestid, foiministryrequestid):
        requestdetails = self.getrequest(foirequestid, foiministryrequestid)
        approvedcfrfee = cfrfeeservice().getapprovedcfrfee(foiministryrequestid)
        cfrfee = cfrfeeservice().getcfrfee(foiministryrequestid)
        payment = paymentservice().getpayment(foirequestid, foiministryrequestid)
        if approvedcfrfee is not None and approvedcfrfee != {}:
            requestdetails['cfrfee'] = approvedcfrfee
            _totaldue = float(approvedcfrfee['feedata']['actualtotaldue']) if float(approvedcfrfee['feedata']['actualtotaldue']) > 0 else float(approvedcfrfee['feedata']['estimatedtotaldue'])
            _balancedue = _totaldue - (float(cfrfee['feedata']['amountpaid']) + float(approvedcfrfee['feedata']['feewaiveramount']))
            requestdetails['cfrfee']['feedata']['amountpaid'] = cfrfee['feedata']['amountpaid']
            requestdetails['cfrfee']['feedata']["balanceDue"] = '{:.2f}'.format(_balancedue)
            if approvedcfrfee['feedata']['actualtotaldue']:
                requestdetails['cfrfee']['feedata']["totalamountdue"] = '{:.2f}'.format(requestdetails['cfrfee']['feedata']["actualtotaldue"])
            else:
                requestdetails['cfrfee']['feedata']["totalamountdue"] = '{:.2f}'.format(requestdetails['cfrfee']['feedata']["estimatedtotaldue"])
            
        if payment is not None and payment != {}:
            paidamount = float(payment['paidamount']) if payment['paidamount'] != None else 0
            requestdetails['cfrfee']['feedata']['paidamount'] = '{:.2f}'.format(paidamount)
            # depositpaid field is only accurate and used for outstanding email and receipts
            requestdetails['cfrfee']['feedata']['depositpaid'] = '{:.2f}'.format(float(cfrfee['feedata']['amountpaid']) - paidamount)
            requestdetails['cfrfee']['feedata']['paymenturl'] = payment['paymenturl']            
            requestdetails['cfrfee']['feedata']['paymentdate'] = payment['created_at'][:10]
        return requestdetails

    def __preparebaseinfo(self,request,foiministryrequestid,requestministry,requestministrydivisions):
        _receiveddate = parse(request['receiveddate'])
        axissyncdatenoneorempty =  self.__noneorempty(requestministry["axissyncdate"]) 
        linkedministryrequests= []
        if "linkedrequests" in requestministry and requestministry["linkedrequests"] is not None:
            linkedministryrequests = self.__assignministrynames(requestministry["linkedrequests"])
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
            'assignedGroupEmail': KeycloakAdminService().processgroupEmail(requestministry["assignedgroup"]),
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
            'originalDueDate':  parse(requestministry['originalldd']).strftime(self.__genericdateformat()) if requestministry['originalldd'] is not None else parse(requestministry['duedate']).strftime(self.__genericdateformat()),            
            'programareaid':requestministry['programarea.programareaid'],
            'bcgovcode':requestministry['programarea.bcgovcode'],
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
            'closedate': parse(requestministry['closedate']).strftime(self.__genericdateformat()) if requestministry['closedate'] is not None else None,
            'subjectCode': subjectcodeservice().getministrysubjectcodename(foiministryrequestid),
            'isofflinepayment': FOIMinistryRequest.getofflinepaymentflag(foiministryrequestid),
            'linkedRequests' : linkedministryrequests,
            'identityVerified':requestministry['identityverified'],
            
        }
        if requestministry['cfrduedate'] is not None:
            baserequestinfo.update({'cfrDueDate':parse(requestministry['cfrduedate']).strftime(self.__genericdateformat())})
        return baserequestinfo
    
    def __assignministrynames(self, linkedrequests):
        areas = programareaservice().getprogramareas()
        if linkedrequests is not None:
            for entry in linkedrequests:
                area = next((a for a in areas if a["programareaid"] == list(entry.values())[0]), None)
                if (area is not None):
                    entry = area["name"]
        return linkedrequests
    
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
                    "eApproval": ministrydivision["eapproval"],
                    "divisionReceivedDate": parse(ministrydivision['divisionreceiveddate']).strftime(self.__genericdateformat()) if ministrydivision['divisionreceiveddate'] is not None else None,
                    } 
                divisions.append(division) 
        return divisions

    
    def getonholdtransition(self, foiministryrequestid):
        onholddate = None
        transitions = FOIMinistryRequest.getrequeststatusById(foiministryrequestid)
        for entry in transitions:
            if entry['requeststatusid'] == 11:
                onholddate = datetimehandler().convert_to_pst(entry['created_at'],'%Y-%m-%d')
            else:
                if onholddate is not None:
                    break
        return onholddate

    def getministryrequest(self, foiministryrequestid):
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
        return requestministry
    
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
