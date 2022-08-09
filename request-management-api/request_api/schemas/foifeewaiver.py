
from marshmallow import EXCLUDE, Schema, fields, validate

"""
This class  consolidates schemas of CFR Fee Waiver Form operations.

__author__      = "nicholas.kan@aot-technologies.com"

"""


class FOIFeeWaiverInabilityDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    hasproof = fields.Bool(data_key="hasproof")
    description = fields.Str(data_key="description")

class FOIFeeWaiverPublicDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    debate = fields.Bool(data_key="debate")
    environment = fields.Bool(data_key="environment")
    disclosing = fields.Bool(data_key="disclosing")
    understanding = fields.Bool(data_key="understanding")
    newpolicy = fields.Bool(data_key="newpolicy")
    financing = fields.Bool(data_key="financing")
    other = fields.Str(data_key="other")
    analysis = fields.Str(data_key="analysis", validate=validate.OneOf(['partial', 'yes', 'no'])) #partial, yes or no
    description = fields.Str(data_key="description")

class FOIFeeWaiverRecommendationSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    waive = fields.Str(data_key="waive", validate=validate.OneOf(['partial', 'yes', 'no'])) #partial, yes or no
    summary = fields.Str(data_key="summary")
    amount = fields.Float(data_key="amount")

class FOIFeeWaiverDecisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    # signature = fields.Str(data_key="signature")
    amount = fields.Float(data_key="amount")

class FOIFeeWaiverFormDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    requesteddate = fields.Str(data_key="requesteddate")
    receiveddate = fields.Str(data_key="receiveddate")
    summary = fields.Str(data_key="summary")
    recordsdescription = fields.Str(data_key="recordsdescription")
    type = fields.Str(data_key="type", validate=validate.OneOf(['public', 'inability']))
    inability = fields.Nested(FOIFeeWaiverInabilityDataSchema)
    public = fields.Nested(FOIFeeWaiverPublicDataSchema)
    disseminate = fields.Bool()
    abletodisseminate = fields.Bool()
    narrow = fields.Bool()
    exceed = fields.Bool()
    timelines = fields.Bool()
    previous = fields.Bool()
    recommendation = fields.Nested(FOIFeeWaiverRecommendationSchema, allow_none=False)

class FOIFeeWaiverMinistryFormDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
    decision = fields.Nested(FOIFeeWaiverDecisionSchema, allow_none=False)

class FOIFeeWaiverIAOSchema(Schema):
    class Meta:
        """Exclude unknown fields in the deserialized output."""
    status = fields.Str(data_key="status", required=True)
    formdata = fields.Nested(FOIFeeWaiverFormDataSchema, allow_none=False)

class FOIFeeWaiverMinistrySchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    status = fields.Str(data_key="status", required=True)
    formdata = fields.Nested(FOIFeeWaiverMinistryFormDataSchema, allow_none=False)