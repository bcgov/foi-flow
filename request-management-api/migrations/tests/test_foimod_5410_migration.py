"""Isolated PostgreSQL tests for FOIMOD-5410's simpler migration.

The target must be the disposable foimod5410-db Docker fixture only.
Run using the existing run_foimod_5410_local.ps1 script.
"""
import importlib.util
import os
from pathlib import Path
import unittest
from urllib.parse import urlsplit

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text

URL = os.environ.get("FOIMOD_5410_TEST_URL", "")
parts = urlsplit(URL)
if (
    parts.hostname != "foimod5410-db"
    or parts.path != "/foimod5410_local"
    or parts.username != "foimod5410"
):
    raise RuntimeError("Refusing fixture tests outside isolated foimod5410-db PostgreSQL database")

MIGRATION = (Path(__file__).resolve().parents[1] / "versions"
             / "b41d590e3a20_foimod_5410_letter_template_cleanup.py")
spec = importlib.util.spec_from_file_location("foimod5410_revision", MIGRATION)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

# Different numeric IDs from DEV/TEST to verify that IDs are not relied upon.
RECORDS = (
    (10040, "AExtension101D", "A - Extension - 10 1 D", "General"),
    (10044, "AOIPCAppConsentTimeExt", "A - OIPC - Applicant Consent Time Extension", "General"),
    (10045, "AOIPCFirstTimeExtension", "A - OIPC - First Time Extension", "General"),
    (10047, "AOIPCSubsequentTimeExt", "A - OIPC - Subsequent Time Extension", "General"),
    (10083, "PAckIndividualandOthOutofProvCountry", "P - Ack - Individual and Others - Out of Province or Country", "Personal"),
    (10172, "PAckIndividualOutofProvinceorCountry", "P - Ack - Individual - Out of Province or Country", "Both"),
)


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(URL)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        with self.engine.begin() as conn:
            conn.execute(text('DROP TABLE IF EXISTS public."Template"'))
            conn.execute(text('''CREATE TABLE public."Template" (
                templateid INTEGER PRIMARY KEY,
                filename TEXT NOT NULL,
                templatename TEXT NOT NULL,
                isactive BOOLEAN NOT NULL,
                requesttype TEXT NOT NULL,
                templatetype TEXT,
                documentpath TEXT NOT NULL,
                encodedcontent TEXT NOT NULL,
                updatedby TEXT,
                updatedat TIMESTAMPTZ
            )'''))
            for templateid, filename, name, request_type in RECORDS:
                conn.execute(text('''INSERT INTO public."Template"
                    (templateid, filename, templatename, isactive, requesttype,
                     templatetype, documentpath, encodedcontent, updatedby, updatedat)
                    VALUES (:id, :filename, :name, TRUE, :requesttype, 'letter',
                            :path, :content, 'previous-auditor', NULL)'''), {
                    "id": templateid, "filename": filename, "name": name,
                    "requesttype": request_type,
                    "path": f"/TEMPLATES/{filename}.docx",
                    "content": f"original-content-{templateid}",
                })

    def snapshot(self):
        with self.engine.connect() as conn:
            return [dict(row) for row in conn.execute(text(
                'SELECT * FROM public."Template" ORDER BY templateid'
            )).mappings().all()]

    def apply(self, direction):
        with self.engine.begin() as conn:
            context = MigrationContext.configure(conn)
            with Operations.context(context):
                getattr(migration, direction)()

    def test_upgrade_and_downgrade_preserve_non_target_fields(self):
        before = self.snapshot()
        self.apply("upgrade")
        after = self.snapshot()
        inactive = {name for _filename, name in migration.DEACTIVATE}
        for old, new in zip(before, after):
            if old["templatename"] in inactive:
                self.assertFalse(new["isactive"])
            elif old["filename"] == migration.OIPC_FILENAME:
                self.assertEqual(new["templatename"], migration.NEW_OIPC_NAME)
                self.assertTrue(new["isactive"])
            else:
                self.assertEqual(new, old)
            for field in ("templateid", "filename", "requesttype", "templatetype",
                          "documentpath", "encodedcontent", "updatedby", "updatedat"):
                self.assertEqual(old[field], new[field], field)
        self.apply("downgrade")
        self.assertEqual(self.snapshot(), before)

    def test_repeated_upgrade_does_not_reactivate_templates(self):
        self.apply("upgrade")
        before = self.snapshot()
        with self.assertLogs(migration.log, level="WARNING"):
            self.apply("upgrade")
        self.assertEqual(self.snapshot(), before)

    def test_previously_inactive_remains_inactive_on_upgrade(self):
        with self.engine.begin() as conn:
            conn.execute(text('''UPDATE public."Template" SET isactive = FALSE
                WHERE filename = 'AExtension101D' '''))
        with self.assertLogs(migration.log, level="WARNING"):
            self.apply("upgrade")
        rows = self.snapshot()
        target = next(r for r in rows if r["filename"] == "AExtension101D")
        self.assertFalse(target["isactive"])

    def test_active_destination_name_skips_rename(self):
        with self.engine.begin() as conn:
            conn.execute(text('''INSERT INTO public."Template"
                (templateid,filename,templatename,isactive,requesttype,templatetype,documentpath,encodedcontent)
                VALUES (99999,'OtherFile','A - OIPC - Time Extension Application',TRUE,'General','letter','/other','other')'''))
        with self.assertLogs(migration.log, level="WARNING"):
            self.apply("upgrade")
        rows = self.snapshot()
        target = next(r for r in rows if r["filename"] == migration.OIPC_FILENAME)
        self.assertEqual(target["templatename"], migration.OLD_OIPC_NAME)
        self.assertTrue(target["isactive"])

    def test_unexpected_name_is_skipped_without_reactivating(self):
        with self.engine.begin() as conn:
            conn.execute(text('''UPDATE public."Template"
                SET templatename = 'Unexpected Name'
                WHERE filename = 'AOIPCSubsequentTimeExt' '''))
        with self.assertLogs(migration.log, level="WARNING"):
            self.apply("upgrade")
        target = next(r for r in self.snapshot() if r["filename"] == "AOIPCSubsequentTimeExt")
        self.assertEqual(target["templatename"], "Unexpected Name")
        self.assertTrue(target["isactive"])

    def test_duplicate_exact_target_rolls_back(self):
        with self.engine.begin() as conn:
            conn.execute(text('''INSERT INTO public."Template"
                (templateid,filename,templatename,isactive,requesttype,templatetype,documentpath,encodedcontent)
                VALUES (99999,'AExtension101D','A - Extension - 10 1 D',TRUE,'General','letter','/other','other')'''))
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "unexpectedly affected 2 rows"):
            self.apply("upgrade")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
