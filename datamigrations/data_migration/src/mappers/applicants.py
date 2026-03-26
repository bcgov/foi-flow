from __future__ import annotations

from mappers.common import parse_optional_datetime


def map_applicant(axis_row: dict, created_by: str = "cfdmigration") -> dict:
    return {
        "firstname": axis_row.get("firstName"),
        "lastname": axis_row.get("lastName"),
        "middlename": axis_row.get("middleName"),
        "dob": parse_optional_datetime(axis_row.get("birthDate")),
        "businessname": axis_row.get("businessName"),
        "createdby": created_by,
    }


def map_applicant_mapping(
    axis_row: dict,
    *,
    foirequestapplicantid: int,
    foirequest_id: int,
    foirequestversion_id: int,
    requestor_type_id: int | None = None,
    created_by: str = "cfdmigration",
) -> dict:
    requestor_type_name = "Self" if int(axis_row.get("MainApplicant", 0)) == 1 else "Applying for other person"
    return {
        "createdby": created_by,
        "requestor_type_name": requestor_type_name,
        "requestortypeid": requestor_type_id,
        "foirequestapplicantid": foirequestapplicantid,
        "foirequest_id": foirequest_id,
        "foirequestversion_id": foirequestversion_id,
        "migrationreference": axis_row["requestid"],
    }
