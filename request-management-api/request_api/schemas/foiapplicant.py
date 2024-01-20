from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE, BLANK_EXCEPTION_MESSAGE
from request_api.schemas.foirequestwrapper import FOIAdditionallPersonalInfoWrapperSchema

class FOIRequestApplicantSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    firstName = fields.Str(data_key="firstName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE, max=50)])    
    middleName = fields.Str(data_key="middleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])    
    lastName = fields.Str(data_key="lastName", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE, max=50)])         
    email = fields.Str(data_key="email",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])      
    businessName = fields.Str(data_key="businessName",allow_none=True, validate=[validate.Length(max=255, error=MAX_EXCEPTION_MESSAGE)]) 
    category = fields.Str(data_key="category", required=True,validate=[validate.Length(min=1, error=BLANK_EXCEPTION_MESSAGE)])

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
    # correctionalServiceNumber = fields.Str(data_key="correctionalServiceNumber",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)]) 
    # publicServiceEmployeeNumber = fields.Str(data_key="publicServiceEmployeeNumber",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)]) 
    
    foiRequestApplicantID = fields.Int(data_key="foiRequestApplicantID",required=False,allow_none=True)
    foirequestID = fields.List(fields.Int(),data_key="foirequestID",required=False,allow_none=False)
    additionalPersonalInfo = fields.Nested(FOIAdditionallPersonalInfoWrapperSchema,required=False,allow_none=True)
    category = fields.Int(data_key="category",required=False,allow_none=True)