from marshmallow import EXCLUDE, Schema, fields, validate

"""
This class  consolidates schemas of bpm operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIMinistryRequestWrapperSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    code = fields.Str(data_key="code")
    name = fields.Str(data_key="name")
    isSelected = fields.Bool(data_key="isSelected")
    
class FOIAdditionallPersonalInfoWrapperSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    childFirstName = fields.Str(data_key="childFirstName",allow_none=True)
    childMiddleName = fields.Str(data_key="childMiddleName",allow_none=True)
    childLastName = fields.Str(data_key="childLastName",allow_none=True)
    childAlsoKnownAs = fields.Str(data_key="childAlsoKnownAs",allow_none=True)
    childBirthDate = fields.Str(data_key="childBirthDate",allow_none=True)
    
    anotherFirstName = fields.Str(data_key="anotherFirstName",allow_none=True)
    anotherMiddleName = fields.Str(data_key="anotherMiddleName",allow_none=True)
    anotherLastName = fields.Str(data_key="anotherLastName",allow_none=True)
    anotherAlsoKnownAs = fields.Str(data_key="anotherAlsoKnownAs",allow_none=True)
    anotherBirthDate = fields.Str(data_key="anotherBirthDate",allow_none=True)
    
    adoptiveMotherFirstName = fields.Str(data_key="adoptiveMotherFirstName",allow_none=True)
    adoptiveMotherLastName = fields.Str(data_key="adoptiveMotherLastName",allow_none=True)
    adoptiveFatherFirstName = fields.Str(data_key="adoptiveFatherFirstName",allow_none=True)
    adoptiveFatherLastName = fields.Str(data_key="adoptiveFatherLastName",allow_none=True)
    
    personalHealthNumber = fields.Str(data_key="personalHealthNumber",allow_none=True)   
    identityVerified = fields.Str(data_key="identityVerified",allow_none=True) 
    
    birthDate = fields.Str(data_key="birthDate",allow_none=True)
    alsoKnownAs = fields.Str(data_key="alsoKnownAs",allow_none=True)
    
class FOIMinistryRequestDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    documentpath = fields.Str(data_key="documentpath",allow_none=False)
    filename = fields.Str(data_key="filename",allow_none=False)
    category = fields.Str(data_key="category",allow_none=False)
class FOIRequestWrapperSchema(Schema):

    BLANK_EXCEPTION_MESSAGE = 'Field cannot be blank'
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    foirawrequestid = fields.Int(data_key="id")
    description = fields.Str(data_key="description", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    requestType = fields.Str(data_key="requestType", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)]) 
    firstName = fields.Str(data_key="firstName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])    
    middleName = fields.Str(data_key="middleName",allow_none=True)    
    lastName = fields.Str(data_key="lastName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])         
    email = fields.Str(data_key="email",allow_none=True)      
    businessName = fields.Str(data_key="businessName",allow_none=True) 
    assignedGroup = fields.Str(data_key="assignedGroup",allow_none=True)
    assignedTo = fields.Str(data_key="assignedTo",allow_none=True)  
    fromDate = fields.Str(data_key="fromDate",allow_none=True)
    toDate = fields.Str(data_key="toDate",allow_none=True)
    dueDate = fields.Str(data_key="dueDate", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    cfrDueDate = fields.Date(data_key="cfrDueDate", required=False,allow_none=True)
    deliveryMode = fields.Str(data_key="deliveryMode", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])   
    receivedMode = fields.Str(data_key="receivedMode", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])   
    receivedDate = fields.Str(data_key="receivedDateUF", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])
    startDate = fields.Str(data_key="requestProcessStart", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])  
    assignedministrygroup = fields.Str(data_key="assignedministrygroup",allow_none=True)
    assignedministryperson = fields.Str(data_key="assignedministryperson",allow_none=True)        

    
    phonePrimary = fields.Str(data_key="phonePrimary",allow_none=True)    
    workPhonePrimary = fields.Str(data_key="workPhonePrimary",allow_none=True)  
    phoneSecondary = fields.Str(data_key="phoneSecondary",allow_none=True)    
    workPhoneSecondary = fields.Str(data_key="workPhoneSecondary",allow_none=True)    
    address = fields.Str(data_key="address",allow_none=True)    
    addressSecondary = fields.Str(data_key="addressSecondary",allow_none=True)    
    city = fields.Str(data_key="city",allow_none=True)    
    province = fields.Str(data_key="province",allow_none=True)    
    postal = fields.Str(data_key="postal",allow_none=True)   
    country = fields.Str(data_key="country",allow_none=True) 
    requeststatusid = fields.Int(data_key="requeststatusid",allow_none=True)
    closedate = fields.Date(data_key="closedate", required=False,allow_none=True)
    closereasonid = fields.Int(data_key="closereasonid",allow_none=True)
    correctionalServiceNumber = fields.Str(data_key="correctionalServiceNumber",allow_none=True) 
    publicServiceEmployeeNumber = fields.Str(data_key="publicServiceEmployeeNumber",allow_none=True) 
  
    selectedMinistries = fields.Nested(FOIMinistryRequestWrapperSchema, many=True)
    additionalPersonalInfo = fields.Nested(FOIAdditionallPersonalInfoWrapperSchema)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, many=True,allow_none=True)
    idNumber = fields.Str(data_key="idNumber",allow_none=True) 

class EditableFOIMinistryRequestWrapperSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    filenumber = fields.Str(data_key="filenumber")
    status = fields.Str(data_key="status")

class EditableFOIRequestWrapperSchema(Schema):
    wfinstanceid = fields.Str(data_key="wfinstanceId",allow_none=True)
    selectedMinistries = fields.Nested(EditableFOIMinistryRequestWrapperSchema, many=True)  

class FOIMinistryRequestDivisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    divisionid = fields.Int(data_key="divisionid")
    stageid = fields.Int(data_key="stageid")

  
class FOIRequestMinistrySchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    assignedministrygroup = fields.Str(data_key="assignedministrygroup",allow_none=True)   
    assignedministryperson = fields.Str(data_key="assignedministryperson",allow_none=True)   
    assignedgroup = fields.Str(data_key="assignedgroup",allow_none=True)   
    assignedto = fields.Str(data_key="assignedto",allow_none=True)   
    requeststatusid = fields.Int(data_key="requeststatusid",allow_none=True)
    divisions = fields.Nested(FOIMinistryRequestDivisionSchema, many=True,allow_none=True)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, many=True,allow_none=True)