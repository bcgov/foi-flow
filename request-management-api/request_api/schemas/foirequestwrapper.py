from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import BLANK_EXCEPTION_MESSAGE, MAX_EXCEPTION_MESSAGE

"""
This class  consolidates schemas of bpm operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIMinistryRequestWrapperSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    code = fields.Str(data_key="code", validate=[validate.Length(max=30, error=MAX_EXCEPTION_MESSAGE)])
    name = fields.Str(data_key="name", validate=[validate.Length(max=255, error=MAX_EXCEPTION_MESSAGE)])
    isSelected = fields.Bool(data_key="isSelected")
    
class FOIAdditionallPersonalInfoWrapperSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    childFirstName = fields.Str(data_key="childFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    childMiddleName = fields.Str(data_key="childMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    childLastName = fields.Str(data_key="childLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    childAlsoKnownAs = fields.Str(data_key="childAlsoKnownAs",allow_none=True)
    childBirthDate = fields.Str(data_key="childBirthDate",allow_none=True)
    
    anotherFirstName = fields.Str(data_key="anotherFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    anotherMiddleName = fields.Str(data_key="anotherMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    anotherLastName = fields.Str(data_key="anotherLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    anotherAlsoKnownAs = fields.Str(data_key="anotherAlsoKnownAs",allow_none=True)
    anotherBirthDate = fields.Str(data_key="anotherBirthDate",allow_none=True)
    
    adoptiveMotherFirstName = fields.Str(data_key="adoptiveMotherFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    adoptiveMotherLastName = fields.Str(data_key="adoptiveMotherLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    adoptiveFatherFirstName = fields.Str(data_key="adoptiveFatherFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    adoptiveFatherLastName = fields.Str(data_key="adoptiveFatherLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    
    personalHealthNumber = fields.Str(data_key="personalHealthNumber",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])   
    #identityVerified = fields.Str(data_key="identityVerified",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)]) 
    
    birthDate = fields.Str(data_key="birthDate",allow_none=True)
    alsoKnownAs = fields.Str(data_key="alsoKnownAs",allow_none=True)
    
class FOIMinistryRequestDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    documentpath = fields.Str(data_key="documentpath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])

class FOIOIPCInquirySchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    inquirydate = fields.Str(data_key="inquirydate",allow_none=True)
    orderno = fields.Str(data_key="orderno",allow_none=True)
    inquiryoutcome = fields.Int(data_key="inquiryoutcome",allow_none=True)

class FOIMinistryRequestOIPCSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    oipcno = fields.Str(data_key="oipcno")
    reviewtypeid = fields.Int(data_key="reviewtypeid")
    reasonid = fields.Int(data_key="reasonid")
    statusid = fields.Int(data_key="statusid")
    outcomeid = fields.Int(data_key="outcomeid",allow_none=True)
    investigator = fields.Str(data_key="investigator",allow_none=True, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])  
    isinquiry = fields.Bool(data_key="isinquiry")
    isjudicialreview = fields.Bool(data_key="isjudicialreview")
    issubsequentappeal = fields.Bool(data_key="issubsequentappeal")
    inquiryattributes = fields.Nested(FOIOIPCInquirySchema, data_key="inquiryattributes", allow_none=True)
    receiveddate = fields.Str(data_key="receiveddate",allow_none=True)
    closeddate = fields.Str(data_key="closeddate",allow_none=True)

class FOIRequestWrapperSchema(Schema):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    foirawrequestid = fields.Int(data_key="id")
    axisSyncDate = fields.Str(data_key="axisSyncDate",allow_none=True)  
    axisRequestId = fields.Str(data_key="axisRequestId",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    axispagecount = fields.Int(data_key="axispagecount",allow_none=True)
    recordspagecount = fields.Int(data_key="recordspagecount",allow_none=True)
    description = fields.Str(data_key="description", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    requestType = fields.Str(data_key="requestType", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)]) 
    firstName = fields.Str(data_key="firstName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE, max=50)])    
    middleName = fields.Str(data_key="middleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])    
    lastName = fields.Str(data_key="lastName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE, max=50)])         
    email = fields.Str(data_key="email",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])      
    businessName = fields.Str(data_key="businessName",allow_none=True, validate=[validate.Length(max=255, error=MAX_EXCEPTION_MESSAGE)]) 
    assignedGroup = fields.Str(data_key="assignedGroup",allow_none=True, validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])
    assignedTo = fields.Str(data_key="assignedTo",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])  
    fromDate = fields.Str(data_key="fromDate",allow_none=True)
    toDate = fields.Str(data_key="toDate",allow_none=True)
    dueDate = fields.Str(data_key="dueDate", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    paymentExpiryDate = fields.Str(data_key="paymentExpiryDate", required=False,allow_none=True)
    cfrDueDate = fields.Date(data_key="cfrDueDate", required=False,allow_none=True)
    originalDueDate = fields.Date(data_key="originalDueDate", required=False,allow_none=True)
    deliveryMode = fields.Str(data_key="deliveryMode", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])   
    receivedMode = fields.Str(data_key="receivedMode", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])   
    receivedDate = fields.Str(data_key="receivedDateUF", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    startDate = fields.Str(data_key="requestProcessStart", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])  
    assignedministrygroup = fields.Str(data_key="assignedministrygroup",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    assignedministryperson = fields.Str(data_key="assignedministryperson",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])        
    assignedToFirstName = fields.Str(data_key="assignedToFirstName",allow_none=True)
    assignedToMiddleName = fields.Str(data_key="assignedToMiddleName",allow_none=True)
    assignedToLastName = fields.Str(data_key="assignedToLastName",allow_none=True)
    assignedministrypersonFirstName = fields.Str(data_key="assignedministrypersonFirstName",allow_none=True)
    assignedministrypersonMiddleName = fields.Str(data_key="assignedministrypersonMiddleName",allow_none=True)
    assignedministrypersonLastName = fields.Str(data_key="assignedministrypersonLastName",allow_none=True)

    reopen = fields.Bool(data_key="reopen",allow_none=True)

    phonePrimary = fields.Str(data_key="phonePrimary",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])    
    workPhonePrimary = fields.Str(data_key="workPhonePrimary",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])  
    phoneSecondary = fields.Str(data_key="phoneSecondary",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])    
    workPhoneSecondary = fields.Str(data_key="workPhoneSecondary",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])    
    address = fields.Str(data_key="address",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])    
    addressSecondary = fields.Str(data_key="addressSecondary",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])    
    city = fields.Str(data_key="city",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])    
    province = fields.Str(data_key="province",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])    
    postal = fields.Str(data_key="postal",allow_none=True, validate=[validate.Length(max=10, error=MAX_EXCEPTION_MESSAGE)])   
    country = fields.Str(data_key="country",allow_none=True) 
    requeststatusid = fields.Int(data_key="requeststatusid",allow_none=True)
    requeststatuslabel = fields.Str(data_key="requeststatuslabel",allow_none=False)
    closedate = fields.Date(data_key="closedate", required=False,allow_none=True)
    closereasonid = fields.Int(data_key="closereasonid",allow_none=True)
    correctionalServiceNumber = fields.Str(data_key="correctionalServiceNumber",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)]) 
    publicServiceEmployeeNumber = fields.Str(data_key="publicServiceEmployeeNumber",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)]) 
    isiaorestricted =   fields.Bool(data_key="isiaorestricted")

    foiRequestApplicantID = fields.Int(data_key="foiRequestApplicantID",required=False,allow_none=True)
    axisapplicantid = fields.Int(data_key="axisApplicantID",required=False,allow_none=True)
    isoipcreview =   fields.Bool(data_key="isoipcreview")
    
    selectedMinistries = fields.Nested(FOIMinistryRequestWrapperSchema, many=True)
    additionalPersonalInfo = fields.Nested(FOIAdditionallPersonalInfoWrapperSchema,required=False,allow_none=True)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, many=True,allow_none=True)
    idNumber = fields.Str(data_key="idNumber",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)]) 
    subjectCode = fields.Str(data_key="subjectCode",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   
    isofflinepayment =   fields.Bool(data_key="isofflinepayment")
    linkedRequests = fields.List(fields.Dict(data_key="linkedRequests", required=False))
    identityVerified = fields.Str(data_key="identityVerified",allow_none=True)

    oipcdetails = fields.Nested(FOIMinistryRequestOIPCSchema, many=True,allow_none=True)


class EditableFOIMinistryRequestWrapperSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    filenumber = fields.Str(data_key="filenumber", validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    status = fields.Str(data_key="status", validate=[validate.Length(max=100, error=MAX_EXCEPTION_MESSAGE)])

class EditableFOIRequestWrapperSchema(Schema):
    wfinstanceid = fields.Str(data_key="wfinstanceId",allow_none=True)
    selectedMinistries = fields.Nested(EditableFOIMinistryRequestWrapperSchema, many=True)

class FOIRequestStatusSchema(Schema):
    nextstatename = fields.Str(data_key="nextStateName",allow_none=True) 

class FOIMinistryRequestDivisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    divisionid = fields.Int(data_key="divisionid")
    stageid = fields.Int(data_key="stageid")
    divisionDueDate = fields.Str(data_key="divisionDueDate",allow_none=True)
    eApproval = fields.Str(data_key="eApproval",allow_none=True, validate=[validate.Length(max=12, error=MAX_EXCEPTION_MESSAGE)])
    divisionReceivedDate = fields.Str(data_key="divisionReceivedDate",allow_none=True)

class CreateMinistrySignOffApprovalSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    approvername = fields.Str(data_key="approverName", allow_none=False)
    approvertitle = fields.Str(data_key="approverTitle", allow_none=False)
    approveddate = fields.Str(data_key="approvedDate", allow_none=False)

  
class FOIRequestMinistrySchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    assignedministrygroup = fields.Str(data_key="assignedministrygroup",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   
    assignedministryperson = fields.Str(data_key="assignedministryperson",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   
    assignedgroup = fields.Str(data_key="assignedGroup",allow_none=True, validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])   
    assignedto = fields.Str(data_key="assignedTo",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   
    requeststatusid = fields.Int(data_key="requeststatusid",allow_none=True)
    requeststatuslabel = fields.Str(data_key="requeststatuslabel",allow_none=True)
    divisions = fields.Nested(FOIMinistryRequestDivisionSchema, many=True,allow_none=True)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, many=True,allow_none=True)
    assignedToFirstName = fields.Str(data_key="assignedToFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedToMiddleName = fields.Str(data_key="assignedToMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedToLastName = fields.Str(data_key="assignedToLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonFirstName = fields.Str(data_key="assignedministrypersonFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonMiddleName = fields.Str(data_key="assignedministrypersonMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonLastName = fields.Str(data_key="assignedministrypersonLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    ministrysignoffapproval = fields.Nested(CreateMinistrySignOffApprovalSchema, data_key="ministrysignoffapproval", allow_none=True)