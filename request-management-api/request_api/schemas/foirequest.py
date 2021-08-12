from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of bpm operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIMinistryRequestSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filenumber = fields.Str(data_key="fileNumber")
    description = fields.Str(data_key="description")
    recordSearchFromDate = fields.Date(data_key="recordSearchFromDate")
    recordSearchToDate = fields.Date(data_key="recordSearchToDate")
    startdate = fields.Date(data_key="startDate")
    duedate = fields.Date(data_key="dueDate")
    assignedto = fields.Str(data_key="assignedTo")
    programareaid = fields.Int(data_key="programAreaId")
    requeststatusid = fields.Int(data_key="requestStatusId")

class FOIContactInformationSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    contacttypeid = fields.Int(data_key="contactTypeId")
    contactinformation = fields.Str(data_key="contactInformation")
    dataformat = fields.Str(data_key="dataFormat")
    
class FOIPersonalAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    personalattributeid = fields.Int(data_key="personalAttributeId")
    attributevalue = fields.Str(data_key="attributeValue")
 
class FOIApplicantSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    firstname = fields.Str(data_key="firstName")
    middlename = fields.Str(data_key="middleName")    
    lastname = fields.Str(data_key="lastName")    
    alsoknownas = fields.Str(data_key="alsoKnownAs")    
    dob = fields.Date(data_key="dob")    
    businessname = fields.Str(data_key="businessName")           
    
class FOIRequestApplicantSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    applicant = fields.Nested(FOIApplicantSchema, many=False)
    requestortypeid = fields.Int(data_key="requestorTypeId")
    
class FOIRequestTypeSchema(Schema):
    requestType = fields.Str(data_key="requestType")
 
class FOIRequestSchema(Schema):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    version = fields.Int(data_key="version")
    requestType = fields.Nested(FOIRequestTypeSchema)
    initialrecordsearchfromdate = fields.DateTime(data_key="recordSearchFromDate")
    initialrecordsearchtodate = fields.DateTime(data_key="recordSearchToDate")
    description = fields.Str(data_key="description")
    receiveddate = fields.DateTime(data_key="receiveddate")
    isactive=fields.Bool(data_key="isactive")
    ministryRequests = fields.Nested(FOIMinistryRequestSchema, many=True)
    contactInformations = fields.Nested(FOIContactInformationSchema, many=True)
    personalAttributes = fields.Nested(FOIPersonalAttributeSchema, many=True)
    requestApplicants = fields.Nested(FOIRequestApplicantSchema, many=True)
    
