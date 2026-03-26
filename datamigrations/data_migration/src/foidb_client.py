from __future__ import annotations

import json


class FoidbClient:
    def __init__(self, connection):
        self.connection = connection
        self._placeholder = self._resolve_placeholder()

    def _resolve_placeholder(self) -> str:
        module_name = type(self.connection).__module__.split(".", 1)[0]
        return "?" if module_name == "pyodbc" else "%s"

    def _query(self, template: str) -> str:
        if self._placeholder == "%s":
            return template
        return template.replace("%s", "?")

    def _execute(self, query: str, params=()):
        cursor = self.connection.cursor()
        cursor.execute(self._query(query), params)
        return cursor

    def begin_request(self) -> None:
        return None

    def commit_request(self) -> None:
        self.connection.commit()

    def rollback_request(self) -> None:
        self.connection.rollback()

    def request_exists(self, request_id: str) -> bool:
        cursor = self._execute(
            'SELECT 1 FROM public."FOIRequests" WHERE migrationreference = %s LIMIT 1',
            (request_id,),
        )
        return cursor.fetchone() is not None

    def find_request_bundle(self, request_id: str) -> dict | None:
        cursor = self._execute(
            """
            SELECT foirequestid, version, foirawrequestid
            FROM public."FOIRequests"
            WHERE migrationreference = %s
            LIMIT 1
            """,
            (request_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            "foirequest_id": row[0],
            "foirequestversion_id": row[1],
            "foirawrequestid": row[2],
        }

    def preview_delete_counts(self, bundle: dict) -> dict:
        foirequest_id = bundle["foirequest_id"]
        version_id = bundle["foirequestversion_id"]
        foirawrequestid = bundle.get("foirawrequestid")

        return {
            "FOIRequestContactInformation": self._count(
                """
                SELECT COUNT(*) FROM public."FOIRequestContactInformation"
                WHERE foirequest_id = %s AND foirequestversion_id = %s
                """,
                (foirequest_id, version_id),
            ),
            "FOIRequestApplicantMappings": self._count(
                """
                SELECT COUNT(*) FROM public."FOIRequestApplicantMappings"
                WHERE foirequest_id = %s AND foirequestversion_id = %s
                """,
                (foirequest_id, version_id),
            ),
            "FOIRequestApplicants": self._count(
                """
                SELECT COUNT(*) FROM public."FOIRequestApplicants"
                WHERE foirequestapplicantid IN (
                    SELECT foirequestapplicantid
                    FROM public."FOIRequestApplicantMappings"
                    WHERE foirequest_id = %s AND foirequestversion_id = %s
                )
                """,
                (foirequest_id, version_id),
            ),
            "FOIMinistryRequests": self._count(
                """
                SELECT COUNT(*) FROM public."FOIMinistryRequests"
                WHERE foirequest_id = %s AND foirequestversion_id = %s
                """,
                (foirequest_id, version_id),
            ),
            "FOIRequests": 1,
            "FOIRawRequests": 1 if foirawrequestid else 0,
        }

    def delete_request_bundle(self, bundle: dict) -> None:
        foirequest_id = bundle["foirequest_id"]
        version_id = bundle["foirequestversion_id"]
        foirawrequestid = bundle.get("foirawrequestid")

        self._execute(
            """
            DELETE FROM public."FOIRequestContactInformation"
            WHERE foirequest_id = %s AND foirequestversion_id = %s
            """,
            (foirequest_id, version_id),
        )
        self._execute(
            """
            DELETE FROM public."FOIRequestApplicantMappings"
            WHERE foirequest_id = %s AND foirequestversion_id = %s
            """,
            (foirequest_id, version_id),
        )
        self._execute(
            """
            DELETE FROM public."FOIRequestApplicants"
            WHERE foirequestapplicantid IN (
                SELECT foirequestapplicantid
                FROM public."FOIRequestApplicantMappings"
                WHERE foirequest_id = %s AND foirequestversion_id = %s
            )
            """,
            (foirequest_id, version_id),
        )
        self._execute(
            """
            DELETE FROM public."FOIMinistryRequests"
            WHERE foirequest_id = %s AND foirequestversion_id = %s
            """,
            (foirequest_id, version_id),
        )
        self._execute(
            """
            DELETE FROM public."FOIRequests"
            WHERE foirequestid = %s AND version = %s
            """,
            (foirequest_id, version_id),
        )
        if foirawrequestid:
            self._execute(
                """
                DELETE FROM public."FOIRawRequests"
                WHERE requestid = %s
                """,
                (foirawrequestid,),
            )

    def resolve_received_mode_id(self, received_mode_name: str) -> int | None:
        return self._fetch_lookup_id('SELECT receivedmodeid FROM public."ReceivedModes" WHERE name = %s LIMIT 1', received_mode_name)

    def resolve_applicant_category_id(self, category_name: str | None) -> int | None:
        if not category_name:
            return None
        return self._fetch_lookup_id(
            'SELECT applicantcategoryid FROM public."ApplicantCategories" WHERE name = %s LIMIT 1',
            category_name,
        )

    def resolve_program_area_id(self, iao_code: str = "CFD") -> int:
        result = self._fetch_lookup_id(
            'SELECT programareaid FROM public."ProgramAreas" WHERE iaocode = %s AND isactive = TRUE LIMIT 1',
            iao_code,
        )
        if result is None:
            raise ValueError(f"Program area not found for iaocode={iao_code}.")
        return result

    def resolve_request_status_id(self, name: str = "Open") -> int:
        result = self._fetch_lookup_id(
            'SELECT requeststatusid FROM public."FOIRequestStatuses" WHERE name = %s AND isactive = TRUE LIMIT 1',
            name,
        )
        if result is None:
            raise ValueError(f"Request status not found for name={name}.")
        return result

    def resolve_requestor_type_id(self, requestor_type_name: str) -> int:
        result = self._fetch_lookup_id(
            'SELECT requestortypeid FROM public."RequestorTypes" WHERE name = %s LIMIT 1',
            requestor_type_name,
        )
        if result is None:
            raise ValueError(f"Requestor type not found for name={requestor_type_name}.")
        return result

    def _fetch_lookup_id(self, query: str, value):
        cursor = self._execute(query, (value,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _count(self, query: str, params) -> int:
        cursor = self._execute(query, params)
        row = cursor.fetchone()
        return row[0] if row else 0

    def insert_raw_request(self, payload: dict) -> dict:
        cursor = self._execute(
            """
            INSERT INTO public."FOIRawRequests" (
                requestrawdata, status, notes, created_at, version, updated_at, assignedto,
                updatedby, sourceofsubmission, assignedgroup, ispiiredacted, createdby,
                requirespayment, closedate, closereasonid, axisrequestid, axissyncdate,
                isiaorestricted, linkedrequests, requeststatuslabel, isconsultflag
            ) VALUES (
                %s::jsonb, %s, %s, NOW(), 1, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s::jsonb, %s, %s
            )
            RETURNING requestid, version
            """,
            (
                json.dumps(payload["requestrawdata"]),
                payload["status"],
                payload["notes"],
                payload["assignedto"],
                payload["updatedby"],
                payload["sourceofsubmission"],
                payload["assignedgroup"],
                payload["ispiiredacted"],
                payload["createdby"],
                payload["requirespayment"],
                payload["closedate"],
                payload["closereasonid"],
                payload["axisrequestid"],
                payload["axissyncdate"],
                payload["isiaorestricted"],
                json.dumps(payload["linkedrequests"]),
                payload["requeststatuslabel"],
                payload["isconsultflag"],
            ),
        )
        row = cursor.fetchone()
        return {"foirawrequest_id": row[0], "version": row[1]}

    def insert_parent_request(self, payload: dict) -> dict:
        cursor = self._execute(
            """
            INSERT INTO public."FOIRequests" (
                version, requesttype, isactive, receiveddate, initialdescription,
                initialrecordsearchfromdate, initialrecordsearchtodate, receivedmodeid,
                applicantcategoryid, created_at, updated_at, createdby, updatedby,
                foirawrequestid, migrationreference
            ) VALUES (1, %s, FALSE, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s)
            RETURNING foirequestid, version
            """,
            (
                payload["requesttype"],
                payload["receiveddate"],
                payload["initialdescription"],
                payload["initialrecordsearchfromdate"],
                payload["initialrecordsearchtodate"],
                payload["receivedmodeid"],
                payload["applicantcategoryid"],
                payload["createdby"],
                payload["updatedby"],
                payload.get("foirawrequestid"),
                payload["migrationreference"],
            ),
        )
        row = cursor.fetchone()
        return {"foirequest_id": row[0], "version": row[1]}

    def insert_ministry_request(self, payload: dict) -> None:
        self._execute(
            """
            INSERT INTO public."FOIMinistryRequests" (
                version, isactive, filenumber, description, recordsearchfromdate, recordsearchtodate,
                startdate, duedate, created_at, updated_at, createdby, updatedby, programareaid,
                requeststatusid, foirequest_id, foirequestversion_id, cfrduedate, axisrequestid,
                axispagecount, linkedrequests, migrationreference, identityverified, originalldd, requeststatuslabel
            ) VALUES (
                1, FALSE, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s::jsonb, %s, %s::jsonb, %s, %s
            )
            """,
            (
                payload["filenumber"],
                payload["description"],
                payload["recordsearchfromdate"],
                payload["recordsearchtodate"],
                payload["startdate"],
                payload["duedate"],
                payload["createdby"],
                payload["updatedby"],
                payload["programareaid"],
                payload["requeststatusid"],
                payload["foirequest_id"],
                payload["foirequestversion_id"],
                payload["cfrduedate"],
                payload["filenumber"],
                str(payload["requestpagecount"]),
                json.dumps(payload["linkedrequests"]),
                payload["migrationreference"],
                json.dumps(payload["identityverified"]),
                payload["originalldd"],
                payload.get("requeststatuslabel", "Open"),
            ),
        )

    def insert_applicant(self, payload: dict) -> int:
        cursor = self._execute(
            """
            INSERT INTO public."FOIRequestApplicants" (
                firstname, lastname, middlename, dob, businessname, created_at, createdby
            ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            RETURNING foirequestapplicantid
            """,
            (
                payload["firstname"],
                payload["lastname"],
                payload["middlename"],
                payload["dob"],
                payload["businessname"],
                payload["createdby"],
            ),
        )
        row = cursor.fetchone()
        return row[0]

    def insert_applicant_mapping(self, payload: dict) -> None:
        self._execute(
            """
            INSERT INTO public."FOIRequestApplicantMappings" (
                created_at, createdby, requestortypeid, foirequestapplicantid,
                foirequest_id, foirequestversion_id, migrationreference
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """,
            (
                payload["createdby"],
                payload["requestortypeid"],
                payload["foirequestapplicantid"],
                payload["foirequest_id"],
                payload["foirequestversion_id"],
                payload["migrationreference"],
            ),
        )

    def insert_contact_information(self, payload: dict) -> None:
        self._execute(
            """
            INSERT INTO public."FOIRequestContactInformation" (
                created_at, createdby, contacttypeid, dataformat, contactinformation,
                foirequest_id, foirequestversion_id
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """,
            (
                payload["createdby"],
                payload["contacttypeid"],
                payload["dataformat"],
                payload["value"],
                payload["foirequest_id"],
                payload["foirequestversion_id"],
            ),
        )
