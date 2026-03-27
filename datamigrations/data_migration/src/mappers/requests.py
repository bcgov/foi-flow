from __future__ import annotations

from mappers.common import parse_optional_datetime, parse_optional_json


def map_parent_request(axis_row: dict, created_by: str = "cfdmigration") -> dict:
    return {
        "requesttype": axis_row["requestType"],
        "receiveddate": parse_optional_datetime(axis_row.get("receivedDate")),
        "initialdescription": axis_row.get("requestdescription"),
        "initialrecordsearchfromdate": parse_optional_datetime(axis_row.get("reqDescriptionFromDate")),
        "initialrecordsearchtodate": parse_optional_datetime(axis_row.get("reqDescriptionToDate")),
        "received_mode_name": axis_row.get("receivedMode") or "Email",
        "applicant_category_name": axis_row.get("category"),
        "migrationreference": axis_row["filenumber"],
        "createdby": created_by,
        "updatedby": created_by,
    }


def map_ministry_request(axis_row: dict, created_by: str = "cfdmigration") -> dict:
    return {
        "filenumber": axis_row["filenumber"],
        "description": axis_row.get("requestdescription"),
        "recordsearchfromdate": parse_optional_datetime(axis_row.get("reqDescriptionFromDate")),
        "recordsearchtodate": parse_optional_datetime(axis_row.get("reqDescriptionToDate")),
        "startdate": parse_optional_datetime(axis_row.get("requestProcessStart")),
        "duedate": parse_optional_datetime(axis_row.get("dueDate")),
        "cfrduedate": parse_optional_datetime(axis_row.get("cfrDueDate")),
        "requestpagecount": int(axis_row.get("requestPageCount") or 0),
        "linkedrequests": parse_optional_json(axis_row.get("linkedRequests")) or [],
        "identityverified": parse_optional_json(axis_row.get("identityVerified")),
        "originalldd": parse_optional_datetime(axis_row.get("originalDueDate")),
        "migrationreference": axis_row["filenumber"],
        "createdby": created_by,
        "updatedby": created_by,
    }
