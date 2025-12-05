import logging
from datetime import datetime
from typing import List, Set, Tuple

from sqlalchemy import select, tuple_, exists
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import aliased, relationship
from sqlalchemy import func
from sqlalchemy import desc
from request_api.models.FOIRequestRecordGroup import FOIRequestRecordGroup, FOIRequestRecordGroups
from .db import db, ma
from .default_method_result import DefaultMethodResult


class FOIRequestRecord(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestRecords'
    # Defining the columns
    recordid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version =db.Column(db.Integer,nullable=False)
    foirequestid =db.Column(db.Integer,  nullable=False)
    ministryrequestid =db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.foiministryrequestid'))
    ministryrequestversion=db.Column(db.Integer, db.ForeignKey('FOIMinistryRequests.version'))
    filename = db.Column(db.Text, unique=False, nullable=True)
    s3uripath = db.Column(db.Text, unique=False, nullable=True)
    attributes = db.Column(JSON, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)
    replacementof = db.Column(db.Integer, unique=False, nullable=False)

    groups = relationship(
        "FOIRequestRecordGroup",
        secondary="FOIRequestRecordGroups",
        back_populates="records",
        lazy="selectin"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def create(cls, records, historical_records=None):
        logging.debug("Saving or Updating FOIRequestRecord: %s", records)

        merged_records = []

        try:
            # 1. Merge main records
            for record in records:
                merged_record = db.session.merge(record)
                merged_records.append(merged_record)

            # 2. Add historical records to the session (if provided)
            if historical_records:
                db.session.add_all(historical_records)

            # 3. Commit the entire transaction atomically
            db.session.commit()

            # SUCCESS PATH: Calculate and return result
            _recordids = {}
            for record in merged_records:
                _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.recordid}

            return DefaultMethodResult(True, 'Records saved/updated', -1, _recordids)

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during FOIRequestRecord save (including history): {e}", exc_info=True)

            # Returning False allows the service layer to handle the transaction failure gracefully.
            return DefaultMethodResult(False, f'Database transaction failed: {str(e)}', -1, None)

    @classmethod
    def bulk_create(cls, records):
        """
        Performs an efficient bulk insert for new records using db.session.add_all().
        This method should only be used for creating initial Version 1 records.
        """
        logging.debug(f"Bulk creating {len(records)} FOIRequestRecords.")

        result = DefaultMethodResult(False, 'Bulk insert failed.', -1, {})

        try:
            # 1. Add all records to the session
            db.session.add_all(records)
            # 2. Commit the transaction
            db.session.commit()
            # 3. Success result calculation (after commit, records now have IDs)
            _recordids = {}
            for record in records:
                _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.recordid}

            result = DefaultMethodResult(True, 'Bulk records created successfully', -1, _recordids)
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during FOIRequestRecord bulk create: {e}", exc_info=True)
            result.message = f"Database bulk insert failed: {str(e)}"

        return result

    @classmethod
    def fetch(cls, foirequestid, ministryrequestid):
        records = []
        try:
            sql = text("""
                       WITH latest_group AS (SELECT DISTINCT
                       ON (rg.record_id)
                           rg.record_id,
                           g.document_set_id,
                           g.ministry_request_id,
                           g.name,
                           g.is_active
                       FROM "FOIRequestRecordGroups" rg
                           JOIN "FOIRequestRecordGroup" g
                       ON g.document_set_id = rg.document_set_id
                       WHERE g.is_active = TRUE
                       ORDER BY rg.record_id, g.document_set_id DESC
                           )
                       SELECT fr1.recordid,
                              fr1.isactive,
                              fr1.filename,
                              fr1.s3uripath,
                              fr1.attributes,
                              json_extract_path_text(fr1.attributes::json, 'batch') AS batchid,
                              fr1.createdby,
                              fr1.created_at,
                              fr1.replacementof,
                              -- group info
                              lg.ministry_request_id                                AS group_ministry_request_id,
                              lg.document_set_id                                    AS group_document_set_id,
                              lg.is_active                                          AS group_is_active,
                              lg.name                                               AS group_name
                       FROM "FOIRequestRecords" fr1
                                LEFT JOIN latest_group lg
                                          ON lg.record_id = fr1.recordid
                       WHERE fr1.foirequestid = :foirequestid
                         AND fr1.ministryrequestid = :ministryrequestid
                         AND fr1.isactive = TRUE
                       ORDER BY fr1.recordid DESC;
                       """)

            rs = db.session.execute(sql, {
                'foirequestid': foirequestid,
                'ministryrequestid': ministryrequestid
            })

            for row in rs:
                # handle replacement file
                originalfile = ""
                originalfilename = ""

                if row["replacementof"] is not None:
                    originalrecord = FOIRequestRecord.getrecordbyid(row["replacementof"])
                    if originalrecord:
                        originalfile = originalrecord.get("s3uripath", "")
                        originalfilename = originalrecord.get("filename", "")

                records.append({
                    "recordid": row["recordid"],
                    "filename": row["filename"],
                    "s3uripath": row["s3uripath"],
                    "attributes": row["attributes"],
                    "batchid": row["batchid"],
                    "createdby": row["createdby"],
                    "created_at": row["created_at"],
                    "replacementof": row["replacementof"],
                    # replacement file
                    "originalfile": originalfile,
                    "originalfilename": originalfilename,
                    # group fields
                    "groupdocumentsetid": row["group_document_set_id"],
                    "groupministryrequestid": row["group_ministry_request_id"],
                    "groupisactive": row["group_is_active"],
                    "groupname": row["group_name"]
                })

        except Exception as ex:
            logging.error(f"Error fetching FOIRequestRecords: {ex}")
            raise
        finally:
            db.session.close()

        return records

    @classmethod
    def getrecordbyid(cls, recordid)->DefaultMethodResult:
        comment_schema = FOIRequestRecordSchema(many=False)
        query = db.session.query(FOIRequestRecord).filter_by(recordid=recordid).first()
        return comment_schema.dump(query)

    @classmethod
    def getrecordsbyid(cls, recordids):
        if not recordids:
            return []

        try:
            rows = (db.session.query(cls)
                .filter(
                    cls.recordid.in_(tuple(recordids)),
                    cls.isactive == True
                )
                .order_by(desc(cls.recordid))
                .all()
            )

            return rows

        except Exception as ex:
            logging.error("Error fetching FOIRequestRecords by id", exc_info=True)
            raise

        finally:
            db.session.close()

    @classmethod
    def get_all_records_by_divisionid(cls, divisionid):
        records = []
        try:
            sql = """SELECT * FROM (SELECT DISTINCT ON (recordid) recordid, version, foirequestid, ministryrequestid, filename, attributes, isactive, replacementof
            FROM public."FOIRequestRecords" ORDER BY recordid ASC, version DESC) records 
            WHERE cast(records.attributes::json -> 'divisions' as text) like '%{"divisionid": """+ divisionid +"""}%' and isactive = 'true' OR cast(records.attributes::json -> 'divisions' as text) like '%{"divisionid": """+ divisionid +""", %}%' and isactive = 'true' 
            """
            result = db.session.execute(text(sql))
            for row in result:
                records.append({"recordid": row["recordid"], "foirequestid": row["foirequestid"], "ministryrequestid": row["ministryrequestid"], "filename": row["filename"], "attributes": row["attributes"], "isactive": row["isactive"], "replacementof": row["replacementof"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return records
    
    @classmethod
    def replace(cls,replacingrecordid,records):
        replacingrecord = db.session.query(FOIRequestRecord).filter_by(recordid=replacingrecordid).order_by(FOIRequestRecord.version.desc()).first()
        replacingrecord.isactive=False
        db.session.commit()
        db.session.add_all(records)
        db.session.commit() 
        _recordids = {}
        for record in records:
            _recordids[record.s3uripath] = {"filename": record.filename, "recordid": record.recordid}
        return DefaultMethodResult(True,'Records replaced', -1, _recordids)
    
    @classmethod
    def getbatchcount(cls, ministryrequestid):
        batchcount = 0
        try:
            sql = """select  count(distinct
                        json_extract_path_text("attributes" ::json,'batch')) AS batch_count
                        FROM "FOIRequestRecords" r
						join (select max(version), recordid
								  from public."FOIRequestRecords"
								  group by recordid) r2 on r2.max = r.version and r2.recordid = r.recordid
                        where ministryrequestid = :ministryrequestid and isactive = true  """
            rs = db.session.execute(text(sql), {'ministryrequestid': ministryrequestid})
            for row in rs:
                batchcount = row["batch_count"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return batchcount

    @classmethod
    def validate_records(
            cls,
            foirequestid: int,
            ministryrequestid: int,
            records: List[int],
    ) -> Set[int]:
        """
        Return subset of recordid that exist, are active,
        and belong to the specified request/ministry.
        """
        if not records:
            return set()

        rows = (
            db.session.query(FOIRequestRecord.recordid)
            .filter(
                FOIRequestRecord.recordid.in_(records),
                FOIRequestRecord.foirequestid == foirequestid,
                FOIRequestRecord.ministryrequestid == ministryrequestid,
                FOIRequestRecord.isactive.is_(True),
            )
            .all()
        )

        return {r[0] for r in rows}

    @classmethod
    def get_records_without_group(
            cls,
            ministryrequestid: int
    ) -> Set[int]:
            """
            Return all active records for the latest version of the ministry request
            that are NOT assigned to any group.
            """

            # 1) Determine latest version automatically
            max_version = (
                db.session.query(db.func.max(FOIRequestRecord.ministryrequestversion))
                .filter(FOIRequestRecord.ministryrequestid == ministryrequestid)
                .scalar()
            )

            if max_version is None:
                return set()

            # 2) Retrieve all records matching latest version and not in any group
            rows = (
                db.session.query(FOIRequestRecord.recordid)
                .filter(
                    FOIRequestRecord.ministryrequestid == ministryrequestid,
                    FOIRequestRecord.ministryrequestversion == max_version,
                    FOIRequestRecord.isactive.is_(True),
                    ~exists().where(
                        FOIRequestRecordGroups.record_id == FOIRequestRecord.recordid
                    ),
                )
                .all()
            )

            return {r[0] for r in rows}


class FOIRequestRecordSchema(ma.Schema):
    class Meta:
        fields = ('recordid','version','foirequestid','ministryrequestid','ministryrequestversion','attributes','filename','s3uripath','created_at','createdby','updated_at','updatedby','replacementof')
