from __future__ import annotations

from datetime import datetime, UTC
import logging

from mappers.applicants import map_applicant, map_applicant_mapping
from mappers.contact_information import map_contact_rows
from mappers.requests import map_ministry_request, map_parent_request


LOGGER = logging.getLogger(__name__)


class RequestMigrator:
    def __init__(
        self,
        *,
        axis_client,
        foidb_client,
        created_by: str = "cfdmigration",
        dry_run: bool = False,
        program_area_code: str = "CFD",
    ):
        self.axis_client = axis_client
        self.foidb_client = foidb_client
        self.created_by = created_by
        self.dry_run = dry_run
        self.program_area_code = program_area_code

    def migrate_request(self, request_id: str) -> dict:
        started_at = datetime.now(UTC).isoformat()

        if self.foidb_client.request_exists(request_id):
            return self._result(
                request_id=request_id,
                status="skipped",
                reason="already migrated",
                started_at=started_at,
                foirequest_id="",
            )

        self.foidb_client.begin_request()
        try:
            parent_row = self.axis_client.fetch_parent_request(request_id)
            if parent_row is None:
                self.foidb_client.rollback_request()
                return self._result(
                    request_id=request_id,
                    status="failed",
                    reason="request not found in AXIS",
                    started_at=started_at,
                    foirequest_id="",
                )

            foirequest = self._insert_request_bundle(request_id, parent_row)

            if self.dry_run:
                self.foidb_client.rollback_request()
                return self._result(
                    request_id=request_id,
                    status="dry-run",
                    reason="validated without commit",
                    started_at=started_at,
                    foirequest_id=foirequest["foirequest_id"],
                )

            self.foidb_client.commit_request()
            return self._result(
                request_id=request_id,
                status="migrated",
                reason="",
                started_at=started_at,
                foirequest_id=foirequest["foirequest_id"],
            )
        except Exception as exc:  # pragma: no cover - covered by behavior tests
            LOGGER.exception("Failed to migrate request %s", request_id)
            self.foidb_client.rollback_request()
            return self._result(
                request_id=request_id,
                status="failed",
                reason=str(exc),
                started_at=started_at,
                foirequest_id="",
            )

    def _insert_request_bundle(self, request_id: str, parent_row: dict) -> dict:
        parent_payload = map_parent_request(parent_row, created_by=self.created_by)
        parent_payload["receivedmodeid"] = self.foidb_client.resolve_received_mode_id(parent_payload["received_mode_name"])
        parent_payload["applicantcategoryid"] = self.foidb_client.resolve_applicant_category_id(
            parent_payload["applicant_category_name"]
        )
        foirequest = self.foidb_client.insert_parent_request(parent_payload)

        ministry_row = self.axis_client.fetch_ministry_request(request_id)
        if ministry_row:
            ministry_payload = map_ministry_request(ministry_row, created_by=self.created_by)
            ministry_payload["programareaid"] = self.foidb_client.resolve_program_area_id(self.program_area_code)
            ministry_payload["requeststatusid"] = self.foidb_client.resolve_request_status_id("Open")
            ministry_payload["foirequest_id"] = foirequest["foirequest_id"]
            ministry_payload["foirequestversion_id"] = foirequest["version"]
            self.foidb_client.insert_ministry_request(ministry_payload)

        for applicant_row in self.axis_client.fetch_applicants(request_id):
            applicant_payload = map_applicant(applicant_row, created_by=self.created_by)
            applicant_id = self.foidb_client.insert_applicant(applicant_payload)
            mapping_payload = map_applicant_mapping(
                applicant_row,
                foirequestapplicantid=applicant_id,
                foirequest_id=foirequest["foirequest_id"],
                foirequestversion_id=foirequest["version"],
                created_by=self.created_by,
            )
            mapping_payload["requestortypeid"] = self.foidb_client.resolve_requestor_type_id(
                mapping_payload["requestor_type_name"]
            )
            self.foidb_client.insert_applicant_mapping(mapping_payload)

        for contact_row in self.axis_client.fetch_contact_information(request_id):
            for contact_payload in map_contact_rows(
                contact_row,
                foirequest_id=foirequest["foirequest_id"],
                foirequestversion_id=foirequest["version"],
                created_by=self.created_by,
            ):
                self.foidb_client.insert_contact_information(contact_payload)

        return foirequest

    @staticmethod
    def _result(*, request_id: str, status: str, reason: str, started_at: str, foirequest_id) -> dict:
        return {
            "request_id": request_id,
            "status": status,
            "reason": reason,
            "foirequest_id": foirequest_id,
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        }
