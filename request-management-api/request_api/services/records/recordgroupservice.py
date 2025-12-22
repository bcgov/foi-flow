# services/record_group_service.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from request_api.models import db, FOIMinistryRequest, FOIRequestRecordGroups
from request_api.models.FOIRequestRecordGroup import FOIRequestRecordGroup
from request_api.models.FOIRequestRecords import FOIRequestRecord
from request_api.schemas.foirequestrecord import FOIRequestCreateGroupSchema

@dataclass
class DefaultMethodResult:
    def __init__(self, success, message, code=-1, data=None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data

class recordgroupservice:
    """Service for creating FOI request record groups."""

    def __init__(self):
        self._create_schema = FOIRequestCreateGroupSchema()

    def create(
        self,
        requestid: int,
        ministryrequestid: int,
        recordgroupschema: Dict[str, Any],
        username: str,
    ) -> DefaultMethodResult:
        """
        Create a group and attach (recordid)  for the given scope.

        recordgroupschema (already loaded by Marshmallow) example:
        {
          "name": "Legal Review Batch",
          "records": [101, 102]
        }
        """
        # --- Ensure ministry request context is valid ---
        ministry_req = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
        if ministry_req is None:
            return DefaultMethodResult(False, "Ministry request not found.", None)

        raw_name = recordgroupschema.get("name", "")
        name = raw_name.strip() or "Document Set 1"
        records: List[int] = recordgroupschema.get("records", []) or []

        try:
            valid_records = self.fetch_valid_records(ministryrequestid, records, requestid)
        except ValueError as e:
            return DefaultMethodResult(False, str(e), 400)

        if FOIRequestRecordGroup.exists_with_name(ministry_request_id=ministryrequestid, name=name):
            return DefaultMethodResult(
                success=False,
                message=f'A group named "{name}" already exists for this request.',
                code=409,
                data={"name": name},
            )

        try:
            group = FOIRequestRecordGroup.create_group(
                ministry_request_id=ministryrequestid,
                request_id=requestid,
                name=name,
                created_by=username,
                records=sorted(valid_records),
            )

            if group is None:
                return DefaultMethodResult(False, "Failed to create group.", code=500)

            data = {
                "group": {
                    "documentsetid": group.document_set_id,
                    "requestid": group.request_id,
                    "name": group.name,
                    "ministryrequestid": group.ministry_request_id,
                    "created_by": group.created_by,
                    "created_at": getattr(group, "created_at", None),
                },
                "records": sorted(valid_records),
            }

            return DefaultMethodResult(
                success=True,
                message="Group created.",
                code=200,
                data=data,
            )

        except SQLAlchemyError:
            current_app.logger.exception("Database error creating FOIRequestRecordGroup")
            return DefaultMethodResult(False, "Database error creating group.", 500)
        except Exception:
            current_app.logger.exception("Unexpected error creating FOIRequestRecordGroup")
            return DefaultMethodResult(False, "Unexpected error creating group.", 500)

    def fetch_valid_records(self, ministryrequestid, records, requestid):
        # Validate requested record IDs
        requested_records: Set[int] = set(records)
        valid_records = FOIRequestRecord.validate_records(
            foirequestid=requestid,
            ministryrequestid=ministryrequestid,
            records=list(requested_records),
        )

        missing_records = sorted(requested_records - valid_records)
        if missing_records:
            raise ValueError(f"Missing or invalid record IDs: {missing_records}")

        return valid_records

    def update(self, requestid: int, ministryrequestid: int, payload: dict, username: str):
        document_set_id = payload.get("documentsetid")
        if not document_set_id:
            return DefaultMethodResult(False, "documentsetid is required.", code=400)

        # Fetch group
        group = FOIRequestRecordGroup.query.filter_by(
            document_set_id=document_set_id,
            request_id=requestid,
            ministry_request_id=ministryrequestid
        ).first()

        if not group:
            return DefaultMethodResult(False, "Group not found.", code=404)

        name = payload.get("name")
        if name:
            group.name = name
            group.updated_by = username
            group.updated_at = datetime.utcnow()

        if "records" in payload:
            try:
                # Normalize & validate incoming record list
                new_records = set(payload.get("records") or [])
                valid_records = self.fetch_valid_records(
                    ministryrequestid,
                    new_records,
                    requestid
                )

                # Records currently assigned to this group
                current_records = FOIRequestRecordGroups.get_record_ids(document_set_id)

                # Delta sets
                to_remove = current_records - valid_records
                to_add = valid_records - current_records

                # ------------------------------------------------------
                # Enforce business rule:
                #    A record may belong to ONLY ONE group at a time.
                #
                #    Remove the "to_add" records from ALL other groups
                #    BEFORE adding them to this group.
                # ------------------------------------------------------
                if to_add:
                    FOIRequestRecordGroups.remove_from_other_groups(
                        document_set_id=document_set_id,
                        record_ids=to_add
                    )

                # Remove unselected records from this group
                FOIRequestRecordGroups.remove_records(
                    document_set_id=document_set_id,
                    record_ids=to_remove
                )

                # Add newly selected records to this group
                FOIRequestRecordGroups.add_records(
                    document_set_id=document_set_id,
                    record_ids=to_add
                )

            except ValueError as e:
                return DefaultMethodResult(False, str(e), 400)

        # Commit once
        db.session.commit()

        return DefaultMethodResult(
            True,
            "Group updated.",
            code=200,
            data={
                "documentsetid": group.document_set_id,
                "name": group.name,
                "records": sorted(payload.get("records", [])),
            },
        )

    def fetch(
            self,
            requestid: int,
            ministryrequestid: int,
            documentsetid=None
    ) -> DefaultMethodResult:
        """
        Retrieve all active record groups for a Ministry Request.
        """

        try:
            # Ensure ministry request exists
            ministry_req = FOIMinistryRequest.getrequestbyministryrequestid(ministryrequestid)
            if ministry_req is None:
                return DefaultMethodResult(False, "Ministry request not found.", 404)

            # Fetch all groups (with records included)
            groups = FOIRequestRecordGroup.get_active_groups_for_request(
                ministry_request_id=ministryrequestid,
                request_id=requestid,
                document_set_id=documentsetid,
                include_records=True,
            )

            # Transform for API response
            result = [
                {
                    "documentsetid": g.document_set_id,
                    "name": g.name,
                    "ministryrequestid": g.ministry_request_id,
                    "is_active": g.is_active,
                    "created_at": g.created_at,
                    "created_by": g.created_by,
                    "updated_at": g.updated_at,
                    "updated_by": g.updated_by,
                    "records": sorted(r.recordid for r in g.records),
                }
                for g in groups
            ]

            return DefaultMethodResult(
                True,
                "Groups retrieved.",
                200,
                result
            )

        except Exception:
            current_app.logger.exception("Error fetching record groups")
            return DefaultMethodResult(False, "Unexpected error fetching groups.", 500)

