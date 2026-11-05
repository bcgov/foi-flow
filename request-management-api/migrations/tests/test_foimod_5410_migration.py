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
    raise RuntimeError(
        "Refusing destructive fixture tests outside isolated "
        "foimod5410-db/foimod5410_local PostgreSQL Docker database"
    )

MIGRATION = Path(__file__).resolve().parents[1] / "versions" / "b41d590e3a20_foimod_5410_letter_template_cleanup.py"
spec = importlib.util.spec_from_file_location("foimod5410_revision", MIGRATION)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

# Deliberately use IDs different from the observed TEST database IDs.
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
            conn.execute(text("""CREATE TABLE public."Template" (
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
            )"""))
            for templateid, filename, name, request_type in RECORDS:
                conn.execute(text("""INSERT INTO public."Template"
                    (templateid, filename, templatename, isactive, requesttype,
                     templatetype, documentpath, encodedcontent, updatedby, updatedat)
                    VALUES (:id, :filename, :name, TRUE, :requesttype, 'letter',
                            :path, :content, 'previous-auditor', NULL)"""), {
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
        expected_inactive = {
            "AExtension101D", "AOIPCAppConsentTimeExt",
            "AOIPCSubsequentTimeExt", "PAckIndividualandOthOutofProvCountry"
        }
        for old, new in zip(before, after):
            if new["filename"] in expected_inactive:
                self.assertFalse(new["isactive"])
                self.assertEqual(old["templatename"], new["templatename"])
            elif new["filename"] == "AOIPCFirstTimeExtension":
                self.assertEqual(new["templatename"], "A - OIPC - Time Extension Application")
                self.assertTrue(new["isactive"])
            else:
                self.assertEqual(new, old)  # protect unrelated template
            for key in ("templateid", "filename", "requesttype", "templatetype",
                        "documentpath", "encodedcontent", "updatedby", "updatedat"):
                self.assertEqual(old[key], new[key], key)
        self.apply("downgrade")
        self.assertEqual(self.snapshot(), before)

    def test_missing_or_unexpected_template_fails_without_partial_update(self):
        with self.engine.begin() as conn:
            conn.execute(text("""UPDATE public."Template"
                SET templatename = 'Unexpected Name'
                WHERE filename = 'AOIPCSubsequentTimeExt' """))
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "unexpected state"):
            self.apply("upgrade")
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_target_display_name_fails_without_update(self):
        with self.engine.begin() as conn:
            conn.execute(text("""INSERT INTO public."Template"
                (templateid,filename,templatename,isactive,requesttype,templatetype,documentpath,encodedcontent)
                VALUES (99999,'OtherFile','A - OIPC - Time Extension Application',TRUE,'General','letter','/other','other')"""))
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "belongs to"):
            self.apply("upgrade")
        self.assertEqual(self.snapshot(), before)

    def test_downgrade_refuses_database_not_yet_upgraded(self):
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "unexpected state"):
            self.apply("downgrade")
        self.assertEqual(self.snapshot(), before)

    def test_duplicate_filename_fails_without_update(self):
        with self.engine.begin() as conn:
            conn.execute(text("""INSERT INTO public."Template"
                (templateid,filename,templatename,isactive,requesttype,templatetype,documentpath,encodedcontent)
                VALUES (99999,'AExtension101D','A - Extension - 10 1 D',TRUE,'General','letter','/other','other')"""))
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "expected exactly one"):
            self.apply("upgrade")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
