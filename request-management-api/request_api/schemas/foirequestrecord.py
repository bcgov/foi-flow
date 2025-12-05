from marshmallow import Schema, fields, validate, EXCLUDE
from dataclasses import dataclass

LENGTH_TOO_LONG_MSG = "{field_name} must be no more than {limit} characters long."

class FOIRequestCreateGroupSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE

    # Group metadata
    name = fields.Str(
        required=True,
        data_key="name",
        validate=[validate.Length(
            max=255,
            error=LENGTH_TOO_LONG_MSG.replace("{limit}", "255").replace("{field_name}", "Name")
        )]
    )
    created_by = fields.Str(
        required=False,
        data_key="created_by",
        validate=[validate.Length(
            max=20,
            error=LENGTH_TOO_LONG_MSG.replace("{limit}", "20").replace("{field_name}", "Created By")
        )]
    )

    records = fields.List(
        fields.Int(),
        data_key="records",
        required=False,
        description="List of record IDs to add to the group",
        validate=[validate.Length(
            max=20,
            error="List of records must contain no more than 20 items."
        )],
        example=[1, 2, 3, 4]
    )

class FOIRequestUpdateGroupSchema(Schema):
    name = fields.String(required=False)
    records = fields.List(fields.Int(), required=False)



