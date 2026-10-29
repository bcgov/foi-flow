"""Isolated source-level regression for the existing receipt and filter rules.

Run from request-management-api with:
    python -B -m unittest discover -s tests/unit -p test_pacific_time.py -v

The application's test conftest requires a running database. These tests execute
the actual side-effect-free functions/blocks from the resource/model sources,
with external request/save services replaced by small fakes. They complement,
and do not replace, deployed API/database integration tests.
"""

import ast
from copy import deepcopy
from datetime import datetime, time, timedelta, timezone
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, unquote_plus, urlencode, urlparse

import holidays
import maya
import pytz
from dateutil import parser
from sqlalchemy import Date, DateTime, String, and_, case, column, func, or_, select, table
from sqlalchemy.dialects import postgresql


SERVICE = Path(__file__).resolve().parents[2]
RESOURCE = SERVICE / "request_api/resources/request.py"
FIXED_NOW = datetime(2026, 11, 2, 23, 31, tzinfo=timezone.utc)


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW.astimezone(tz) if tz else FIXED_NOW.astimezone().replace(tzinfo=None)

    @classmethod
    def today(cls):
        return cls.now()


def load_receipt_logic():
    tree = ast.parse(RESOURCE.read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 and node.name in ("_skiptoworkday", "_getholidays", "_isholiday")]
    constants = [node for node in tree.body if isinstance(node, ast.Assign)
                 and any(getattr(target, "id", None) in ("LONG_DATE_FORMAT", "SHORT_DATE_FORMAT")
                         for target in node.targets)]
    resource = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                    and node.name == "FOIRawRequests")
    post = deepcopy(next(node for node in resource.body if isinstance(node, ast.FunctionDef)
                         and node.name == "post"))
    post.decorator_list = []
    namespace = {"datetime": FixedDatetime, "timedelta": timedelta, "holidays": holidays,
                 "pytz": pytz, "os": os, "BusinessException": type("BusinessException", (Exception,), {})}
    module = ast.fix_missing_locations(ast.Module(body=constants + functions + [post], type_ignores=[]))
    exec(compile(module, str(RESOURCE), "exec"), namespace)
    return namespace


def notification_bounds(filename, start, end):
    path = SERVICE / "request_api/models" / filename
    tree = ast.parse(path.read_text())
    method_name = "getbasequery" if filename == "FOIRawRequestNotificationUsers.py" else "geteventsubquery"
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                  and node.name == method_name)
    # Execute the production eventDate conversion before its ORM query is built.
    conversion = next(node for node in method.body if isinstance(node, ast.If)
                      and isinstance(node.test, ast.Compare)
                      and getattr(node.test.left, "id", None) == "daterangetype"
                      and getattr(node.test.comparators[0], "value", None) == "eventDate")
    namespace = {"datetime2": datetime, "time": time, "pytz": pytz,
                 "current_app": SimpleNamespace(config={"LEGISLATIVE_TIMEZONE": "America/Vancouver"}),
                 "daterangetype": "eventDate", "fromdate": start, "todate": end}
    module = ast.fix_missing_locations(ast.Module(body=[conversion], type_ignores=[]))
    exec(compile(module, str(path), "exec"), namespace)
    return namespace["fromdate"], namespace["todate"]


class PacificReceiptTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"FOI_ADDITIONAL_HOLIDAYS": "", "FOI_INVALID_HOLIDAYS": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.logic = load_receipt_logic()

    def submit(self, payload):
        captured = {}

        def save(**kwargs):
            captured.update(deepcopy(kwargs["requestdatajson"]))
            return SimpleNamespace(success=True, message="Saved", identifier=1)

        self.logic["request"] = SimpleNamespace(get_json=lambda: {"requestData": deepcopy(payload)})
        self.logic["RequestDeduplicationService"] = lambda _: SimpleNamespace(dedupe_service=lambda: False)
        self.logic["rawrequestservice"] = lambda: SimpleNamespace(saverawrequest=save)
        self.logic["documentservice"] = lambda: SimpleNamespace(uploadpersonaldocuments=lambda *args: None)
        body, status = self.logic["post"]()
        self.assertEqual(status, 200)
        self.assertTrue(body["status"])
        return captured

    def test_missing_received_date_uses_vancouver_before_cutoff_decision(self):
        saved = self.submit({})
        self.assertEqual(saved["receivedDate"], "2026-11-03")
        self.assertEqual(saved["receivedDateUF"], "2026-11-03 00:00:00")

    def test_supplied_received_wall_time_is_preserved(self):
        for supplied in ("2026-11-02 09:15:00", "2025-01-15 12:00:00"):
            with self.subTest(supplied=supplied):
                saved = self.submit({"receivedDateUF": supplied})
                self.assertEqual(saved["receivedDateUF"], supplied)

    def test_cutoff_preserves_existing_minute_policy(self):
        for value, expected in (("16:29:00", "2026-11-02"), ("16:30:00", "2026-11-02"),
                                ("16:30:59", "2026-11-02"), ("16:31:00", "2026-11-03")):
            with self.subTest(value=value):
                saved = self.submit({"receivedDateUF": "2026-11-02 " + value})
                self.assertEqual(saved["receivedDate"], expected)

    def test_weekends_and_holidays(self):
        for value, expected in (("2026-11-07 09:00:00", "2026-11-09"),
                                ("2026-11-11 09:00:00", "2026-11-12"),
                                # Preserve the existing extra-day rule for a holiday on a weekend.
                                ("2026-12-25 09:00:00", "2026-12-29")):
            with self.subTest(value=value):
                result = self.logic["_skiptoworkday"](value)
                self.assertEqual(result.strftime("%Y-%m-%d"), expected)

    def test_holidays_follow_the_received_year_including_rollover(self):
        for value, expected in (("2027-01-01 09:00:00", "2027-01-04"),
                                ("2026-12-31 16:31:00", "2027-01-04"),
                                ("2025-01-01 09:00:00", "2025-01-02")):
            with self.subTest(value=value):
                result = self.logic["_skiptoworkday"](value)
                self.assertEqual(result.strftime("%Y-%m-%d"), expected)

    def test_additional_holiday_placeholder_follows_received_year(self):
        with patch.dict(os.environ, {"FOI_ADDITIONAL_HOLIDAYS": "XXXX-11-12"}):
            result = self.logic["_skiptoworkday"]("2027-11-12 09:00:00")
            self.assertEqual(result.strftime("%Y-%m-%d"), "2027-11-15")


class PacificNotificationBoundaryTests(unittest.TestCase):
    def test_both_notification_branches_use_correct_inclusive_day_bounds(self):
        cases = (("2025-01-15", "2025-01-15T08:00:00+00:00", "2025-01-16T08:00:00+00:00"),
                 ("2026-03-08", "2026-03-08T08:00:00+00:00", "2026-03-09T07:00:00+00:00"),
                 ("2026-11-01", "2026-11-01T07:00:00+00:00", "2026-11-02T07:00:00+00:00"),
                 ("2026-11-02", "2026-11-02T07:00:00+00:00", "2026-11-03T07:00:00+00:00"),
                 ("2027-01-15", "2027-01-15T07:00:00+00:00", "2027-01-16T07:00:00+00:00"))
        for filename in ("FOIRequestNotificationUsers.py", "FOIRawRequestNotificationUsers.py"):
            for day, expected_start, expected_next in cases:
                with self.subTest(branch=filename, day=day):
                    start, end = notification_bounds(filename, day, day)
                    self.assertEqual(start, datetime.fromisoformat(expected_start))
                    self.assertEqual(end, datetime.fromisoformat(expected_next) - timedelta(microseconds=1))
                    for instant, included in ((start - timedelta(microseconds=1), False),
                                              (start, True), (end, True),
                                              (end + timedelta(microseconds=1), False)):
                        self.assertEqual(start <= instant <= end, included)

    def test_date_objects_keep_the_same_boundary_contract(self):
        day = datetime(2026, 11, 2).date()
        for filename in ("FOIRequestNotificationUsers.py", "FOIRawRequestNotificationUsers.py"):
            with self.subTest(branch=filename):
                start, end = notification_bounds(filename, day, day)
                self.assertEqual(start.isoformat(), "2026-11-02T07:00:00+00:00")
                self.assertEqual(end.isoformat(), "2026-11-03T06:59:59.999999+00:00")


class PacificConsumerTests(unittest.TestCase):
    def test_paybc_transaction_and_ledger_dates_use_the_bc_day(self):
        path = SERVICE / "request_api/services/fee_service.py"
        tree = ast.parse(path.read_text())
        method = deepcopy(next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
                               and node.name == "_get_paybc_url"))
        namespace = {
            "datetime": FixedDatetime, "pytz": pytz, "urlencode": urlencode, "unquote_plus": unquote_plus,
            "FeeCode": object, "RevenueAccount": SimpleNamespace(find_by_id=lambda _: object()),
            "FeeType": SimpleNamespace(application=SimpleNamespace(value="APP"), processing=SimpleNamespace(value="CFR")),
            "HashService": SimpleNamespace(encode=lambda _: "synthetic-unit-test-hash"),
            "current_app": SimpleNamespace(config={"LEGISLATIVE_TIMEZONE": "America/Vancouver",
                "FOI_WEB_PAY_URL": "https://example.invalid/", "PAYBC_REF_NUMBER": "test",
                "PAYBC_PORTAL_URL": "https://example.invalid/pay"}),
        }
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(path), "exec"), namespace)
        fee_code = SimpleNamespace(code="APP", revenue_account_id=1)
        service = SimpleNamespace(fee_code=fee_code, payment=SimpleNamespace(request_id=1, payment_id=1, total=5),
                                  _get_transaction_number=lambda: "TEST1", _get_gl_coding=lambda *args: "test")
        for raw, expected in (("2025-01-15T07:30:00+00:00", "2025-01-14"),
                              ("2026-11-03T07:30:00+00:00", "2026-11-03"),
                              ("2027-01-15T07:30:00+00:00", "2027-01-15")):
            with self.subTest(utc=raw), patch(__name__ + ".FIXED_NOW", datetime.fromisoformat(raw)):
                query = parse_qs(urlparse(namespace["_get_paybc_url"](service, fee_code, "return")).query)
                self.assertEqual(query["trnDate"], [expected])
                self.assertEqual(query["glDate"], [expected])

    def test_common_maya_clock_and_conversion_preserve_history_and_instants(self):
        path = SERVICE / "request_api/utils/commons/datetimehandler.py"
        tree = ast.parse(path.read_text())
        handler = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "datetimehandler")
        namespace = {"maya": maya, "datetime": datetime}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[handler], type_ignores=[])), str(path), "exec"), namespace)
        utility = namespace["datetimehandler"]()
        for raw, expected in (("2025-01-15T20:00:00+00:00", "2025-01-15 12:00:00"),
                              ("2026-11-03T07:30:00+00:00", "2026-11-03 00:30:00"),
                              ("2027-01-15T19:00:00+00:00", "2027-01-15 12:00:00")):
            with self.subTest(utc=raw), patch.object(maya, "now", return_value=maya.parse(raw)):
                instant = datetime.fromisoformat(raw)
                self.assertEqual(utility.gettoday("%Y-%m-%d %H:%M:%S"), expected)
                self.assertEqual(utility.now().astimezone(timezone.utc), instant)
                self.assertEqual(utility.convert_to_pst(instant, "%Y-%m-%d %H:%M:%S"), expected)


if __name__ == "__main__":
    unittest.main()
