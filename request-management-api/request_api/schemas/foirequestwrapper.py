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
    
    birthDate = fields.Str(data_key="birthDate",allow_none=True)
    alsoKnownAs = fields.Str(data_key="alsoKnownAs",allow_none=True)
    
        
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
    fromDate = fields.Str(data_key="fromDate",allow_none=True)
    toDate = fields.Str(data_key="toDate",allow_none=True)
    dueDate = fields.Str(data_key="dueDate",allow_none=True)
    deliveryMode = fields.Str(data_key="deliveryMode",allow_none=True)    
    receivedMode = fields.Str(data_key="receivedMode",allow_none=True)    
    receivedDate = fields.Str(data_key="receivedDateUF",allow_none=True)    
    
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

    
