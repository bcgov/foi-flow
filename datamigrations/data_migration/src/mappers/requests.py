from __future__ import annotations

from mappers.common import parse_optional_datetime, parse_optional_json


def map_raw_request(axis_row: dict, created_by: str = "cfdmigration") -> dict:
    return {
        "requestrawdata": axis_row,
        "status": axis_row.get("status"),
        "notes": axis_row.get("notes"),
        "assignedto": axis_row.get("assignedTo"),
        "sourceofsubmission": axis_row.get("receivedMode"),
        "assignedgroup": axis_row.get("assignedGroup"),
        "ispiiredacted": axis_row.get("isPIIRedacted", False),
        "createdby": created_by,
        "updatedby": created_by,
        "requirespayment": axis_row.get("requiresPayment", False),
        "closedate": parse_optional_datetime(axis_row.get("closedDate")),
        "closereasonid": axis_row.get("closeReasonId"),
        "axisrequestid": axis_row["filenumber"],
        "axissyncdate": parse_optional_datetime(axis_row.get("axisSyncDate")),
        "isiaorestricted": axis_row.get("isIAORestricted", False),
        "linkedrequests": parse_optional_json(axis_row.get("linkedRequests")) or [],
        "requeststatuslabel": axis_row.get("status") or "Open",
        "isconsultflag": axis_row.get("isConsultFlag", False),
    }


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
