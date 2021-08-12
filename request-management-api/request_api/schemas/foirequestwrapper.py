from marshmallow import EXCLUDE, Schema, fields

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
    childFirstName = fields.Str(data_key="childFirstName")
    childMiddleName = fields.Str(data_key="childMiddleName")
    childLastName = fields.Str(data_key="childLastName")
    childAlsoKnownAs = fields.Str(data_key="childAlsoKnownAs")
    childBirthDate = fields.Str(data_key="childBirthDate")
    
    anotherFirstName = fields.Str(data_key="anotherFirstName")
    anotherMiddleName = fields.Str(data_key="anotherMiddleName")
    anotherLastName = fields.Str(data_key="anotherLastName")
    anotherAlsoKnownAs = fields.Str(data_key="anotherAlsoKnownAs")
    anotherBirthDate = fields.Str(data_key="anotherBirthDate")
    
    adoptiveMotherFirstName = fields.Str(data_key="adoptiveMotherFirstName")
    adoptiveMotherLastName = fields.Str(data_key="adoptiveMotherLastName")
    adoptiveFatherFirstName = fields.Str(data_key="adoptiveFatherFirstName")
    adoptiveFatherLastName = fields.Str(data_key="adoptiveFatherLastName")
    
    birthDate = fields.Str(data_key="birthDate")
    alsoKnownAs = fields.Str(data_key="alsoKnownAs")
    
        
class FOIRequestWrapperSchema(Schema):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    foirawrequestid = fields.Int(data_key="id")
    description = fields.Str(data_key="description")
    category = fields.Str(data_key="category")
    requestType = fields.Str(data_key="requestType") 
    firstName = fields.Str(data_key="firstName",allow_none=True)    
    middleName = fields.Str(data_key="middleName",allow_none=True)    
    lastName = fields.Str(data_key="lastName",allow_none=True)     
    email = fields.Str(data_key="email",allow_none=True)      
    businessName = fields.Str(data_key="businessName",allow_none=True) 
    assignedTo = fields.Str(data_key="assignedTo",allow_none=True)    
    fromDate = fields.DateTime(data_key="fromDate",allow_none=True)    
    toDate = fields.DateTime(data_key="toDate",allow_none=True)    
    dueDate = fields.Date(data_key="dueDate",allow_none=True)    
    deliveryMode = fields.Str(data_key="deliveryMode",allow_none=True)    
    receivedMode = fields.Str(data_key="receivedMode",allow_none=True)    
    receivedDate = fields.Date(data_key="receivedDate",allow_none=True)    
    isactive=fields.Bool(data_key="isactive",allow_none=True)    
    
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

    
    selectedMinistries = fields.Nested(FOIMinistryRequestWrapperSchema, many=True)
    additionalPersonalInfo = fields.Nested(FOIAdditionallPersonalInfoWrapperSchema)

    
