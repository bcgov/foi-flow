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
 
class FOIRequestWrapperSchema(Schema):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    foirawrequestid = fields.Int(data_key="id")
    description = fields.Str(data_key="description")
    category = fields.Str(data_key="category")
    requestType = fields.Str(data_key="requestType") 
    firstName = fields.Str(data_key="firstName")
    middleName = fields.Str(data_key="middleName")    
    lastName = fields.Str(data_key="lastName") 
    email = fields.Str(data_key="email")  
    businessName = fields.Str(data_key="businessName")
    assignedTo = fields.Str(data_key="assignedTo")
    fromDate = fields.DateTime(data_key="fromDate")
    toDate = fields.DateTime(data_key="toDate")
    dueDate = fields.Date(data_key="dueDate")
    deliveryMode = fields.Int(data_key="deliveryMode")
    receivedMode = fields.Int(data_key="receivedMode")
    receivedDate = fields.Date(data_key="receivedDate")
    isactive=fields.Bool(data_key="isactive")
    selectedMinistries = fields.Nested(FOIMinistryRequestWrapperSchema, many=True)

    
