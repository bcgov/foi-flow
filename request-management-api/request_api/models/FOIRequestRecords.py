import logging
from datetime import datetime
from typing import List, Set, Tuple

from sqlalchemy import select, tuple_
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy import desc

from .db import db, ma
from .default_method_result import DefaultMethodResult


class FOIRequestRecord(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestRecords'
    # Defining the columns
    recordid = db.Column(db.Integer, primary_key=True,autoincrement=True)
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
            fr1 = aliased(FOIRequestRecord)  # current record
            fr2 = aliased(FOIRequestRecord)  # original record (replacementof)

            # If 'attributes' is JSON/JSONB in SQLAlchemy, you can do:
            #   batch_expr = fr1.attributes['batch'].astext.label("batchid")
            # If it's TEXT storing JSON, use a func/json operator like below (Postgres):
            batch_expr = func.json_extract_path_text(
                fr1.attributes.cast(db.JSON), 'batch'
            ).label("batchid")

            query = (
                db.session.query(
                    fr1.recordid,
                    fr1.filename,
                    fr1.s3uripath,
                    fr1.attributes.label("attributes"),
                    batch_expr,
                    fr1.createdby,
                    fr1.created_at,
                    fr1.replacementof,
                    fr2.s3uripath.label("originalfile"),
                    fr2.filename.label("originalfilename"),
                )
                .outerjoin(fr2, fr1.replacementof == fr2.recordid)
                .filter(
                    fr1.foirequestid == foirequestid,
                    fr1.ministryrequestid == ministryrequestid,
                    fr1.isactive.is_(True),
                )
                .order_by(fr1.recordid.desc())
            )

            for row in query.all():
                records.append({
                    "recordid": row.recordid,
                    "filename": row.filename,
                    "s3uripath": row.s3uripath,
                    "attributes": row.attributes,
                    "batchid": row.batchid,
                    "createdby": row.createdby,
                    "created_at": row.created_at,
                    "replacementof": row.replacementof,
                    "originalfile": row.originalfile or "",
                    "originalfilename": row.originalfilename or "",
                })

        except Exception as ex:
            logging.error(ex)
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

        logging.info("getrecordsbyid",recordids)
        print("getrecordsbyid")
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
        pairs: List[Tuple[int, int]],
    ) -> Set[Tuple[int, int]]:
        """
        Return subset of (recordid, version) that exist, are active,
        and belong to the specified request/ministry.
        """
        if not pairs:
            return set()

        stmt = (
            select(FOIRequestRecord.recordid, FOIRequestRecord.version)
            .where(
                tuple_(FOIRequestRecord.recordid, FOIRequestRecord.version).in_(pairs),
                FOIRequestRecord.foirequestid == foirequestid,
                FOIRequestRecord.ministryrequestid == ministryrequestid,
                FOIRequestRecord.isactive.is_(True),
            )
        )
        rows = db.session.execute(stmt).all()
        return {(r[0], r[1]) for r in rows}

class FOIRequestRecordSchema(ma.Schema):
    class Meta:
        fields = ('recordid','version','foirequestid','ministryrequestid','ministryrequestversion','attributes','filename','s3uripath','created_at','createdby','updated_at','updatedby','replacementof')
