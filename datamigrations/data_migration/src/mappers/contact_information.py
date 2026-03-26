from __future__ import annotations


def map_contact_rows(axis_row: dict, *, foirequest_id: int, foirequestversion_id: int, created_by: str = "cfdmigration") -> list[dict]:
    contact_rows: list[dict] = []

    email = axis_row.get("email")
    if email:
        contact_rows.append(
            {
                "foirequest_id": foirequest_id,
                "foirequestversion_id": foirequestversion_id,
                "contacttypeid": 1,
                "dataformat": "email",
                "value": email,
                "createdby": created_by,
            }
        )

    phone = axis_row.get("mobile") or axis_row.get("home") or axis_row.get("work1")
    if phone:
        contact_rows.append(
            {
                "foirequest_id": foirequest_id,
                "foirequestversion_id": foirequestversion_id,
                "contacttypeid": 2,
                "dataformat": "phone",
                "value": phone,
                "createdby": created_by,
            }
        )

    return contact_rows
