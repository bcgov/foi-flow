import logging
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import pytest

from request_api.services.communicationwrapperservice import communicationwrapperservice


# ---------------------------------------------------------------------------
# Shared helpers — extracted to satisfy Sonar duplication rules and to keep
# individual test bodies focused on the behaviour they exercise.
# ---------------------------------------------------------------------------

_PAYLOAD_BASE = {
    "correspondencemessagejson": '{"body":"hi"}',
    "attributes": [{}],
    "correspondencesubject": "S",
    "templatename": "GENERIC",
    "templateid": None,
    "emails": ["a@x.com"],
}


def _make_payload(attachments):
    """Return a fresh applicantcorrespondencelog payload with the given attachments."""
    return {**_PAYLOAD_BASE, "attachments": list(attachments)}


def _saved_attachments(mock_appservice):
    """Pull the attachments the service passed to saveapplicantcorrespondencelog."""
    call = mock_appservice.return_value.saveapplicantcorrespondencelog.call_args
    saved_log = (
        call.args[2] if len(call.args) >= 3
        else call.kwargs["applicantcorrespondencelog"]
    )
    return saved_log["attachments"]


def _sent_attachments(mock_emailservice):
    """Pull the attachments the service passed to communicationemailservice.send."""
    sent_log = mock_emailservice.return_value.send.call_args.args[1]
    return sent_log["attachments"]


def _run_send_email(payload, ministryrequestid=99):
    communicationwrapperservice().send_email(
        requestid=1, rawrequestid=None, ministryrequestid=ministryrequestid,
        applicantcorrespondencelog=payload,
    )


@pytest.fixture
def sendemail_mocks():
    """Stack the four patches send_email needs, with sane default returns.

    Yields a SimpleNamespace with attributes: auth, email, app, resolve.
    Individual tests override .resolve.return_value as needed.
    """
    with patch("request_api.services.communicationwrapperservice.AuthHelper") as mock_auth, \
         patch("request_api.services.communicationwrapperservice.communicationemailservice") as mock_email, \
         patch("request_api.services.communicationwrapperservice.applicantcorrespondenceservice") as mock_app, \
         patch.object(communicationwrapperservice, "_resolve_ownership_coords") as mock_resolve:
        mock_auth.getuserid.return_value = "tester"
        mock_app.return_value.saveapplicantcorrespondencelog.return_value = MagicMock(
            success=True, identifier=42, message="ok"
        )
        tpl = MagicMock()
        tpl.name = "GENERIC"
        mock_app.return_value.gettemplatebyid.return_value = tpl
        mock_email.return_value.send.return_value = {
            "success": True, "from_email": "noreply@gov.bc.ca",
        }
        yield SimpleNamespace(
            auth=mock_auth, email=mock_email, app=mock_app, resolve=mock_resolve,
        )


# ---------------------------------------------------------------------------
# Validator: single-value (string) API — the original contract.
# ---------------------------------------------------------------------------

class TestValidateAttachmentOwnership:
    def test_valid_attachment_is_retained(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ack.pdf",
             "url": "https://bucket.example/forms-bucket/MIN/MIN-2026-00001/ack.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == attachments

    def test_foreign_attachment_is_rejected(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ours.pdf",
             "url": "https://bucket.example/forms-bucket/MIN/MIN-2026-00001/ours.pdf"},
            {"filename": "leaked.pdf",
             "url": "https://bucket.example/forms-bucket/OTHER/OTHER-2026-99999/leaked.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert len(result) == 1
        assert result[0]["filename"] == "ours.pdf"

    def test_rejection_is_logged_as_warning(self, caplog):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "leaked.pdf",
             "url": "https://bucket.example/forms-bucket/OTHER/OTHER-2026-99999/leaked.pdf"},
        ]
        with caplog.at_level(logging.WARNING):
            svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert any(
            "Attachment ownership violation" in rec.getMessage() and "leaked.pdf" in rec.getMessage()
            for rec in caplog.records
        )

    def test_documenturipath_field_is_also_checked(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ack.pdf",
             "documenturipath": "https://bucket.example/forms-bucket/MIN/MIN-2026-00001/ack.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == attachments

    def test_empty_or_missing_url_is_rejected(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "no-url.pdf"},
            {"filename": "empty.pdf", "url": ""},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == []

    def test_match_is_case_insensitive(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ack.pdf",
             "url": "https://bucket.example/forms-bucket/min/min-2026-00001/ack.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == attachments

    def test_querystring_containing_prefix_does_not_match(self):
        """A malicious/misplaced querystring must not satisfy ownership."""
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "leaked.pdf",
             "url": "https://bucket.example/forms-bucket/OTHER/OTHER-2026-99999/leaked.pdf"
                    "?ref=/MIN/MIN-2026-00001/x"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == []

    def test_partial_segment_does_not_match(self):
        """MIN-2026-00001 must not match a request whose number is MIN-2026-000010."""
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "leaked.pdf",
             "url": "https://bucket.example/forms-bucket/MIN/MIN-2026-000010/leaked.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == []

    def test_percent_encoded_path_is_matched(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ack.pdf",
             "url": "https://bucket.example/forms-bucket/%4D%49%4E/MIN-2026-00001/ack.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == attachments

    def test_raw_s3_key_without_scheme_is_matched(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ack.pdf",
             "url": "forms-bucket/MIN/MIN-2026-00001/ack.pdf"},
        ]
        result = svc._validate_attachment_ownership(attachments, "MIN", "MIN-2026-00001")
        assert result == attachments


# ---------------------------------------------------------------------------
# send_email end-to-end: attachments filtered through _resolve_ownership_coords
# ---------------------------------------------------------------------------

class TestSendEmailStripsForeignAttachments:
    def test_foreign_attachment_never_saved_or_sent(self, sendemail_mocks):
        sendemail_mocks.resolve.return_value = ("MIN", {"MIN-2026-00001"})
        payload = _make_payload([
            {"filename": "ours.pdf",
             "url": "https://bucket/forms/MIN/MIN-2026-00001/ours.pdf"},
            {"filename": "leaked.pdf",
             "url": "https://bucket/forms/OTHER/OTHER-2026-99999/leaked.pdf"},
        ])

        _run_send_email(payload)

        assert [a["filename"] for a in _saved_attachments(sendemail_mocks.app)] == ["ours.pdf"]
        assert [a["filename"] for a in _sent_attachments(sendemail_mocks.email)] == ["ours.pdf"]

    def test_no_attachments_skips_ownership_resolution(self, sendemail_mocks):
        """When there are no attachments the ownership check must not run any lookup."""
        _run_send_email(_make_payload([]))
        sendemail_mocks.resolve.assert_not_called()

    def test_fails_closed_when_ownership_coordinates_cannot_be_resolved(
        self, sendemail_mocks, caplog,
    ):
        """If we cannot resolve ministrycode/requestnumbers, drop all attachments."""
        sendemail_mocks.resolve.return_value = (None, set())
        payload = _make_payload([
            {"filename": "unknown.pdf",
             "url": "https://bucket/forms/WHO/KNOWS/unknown.pdf"},
        ])

        with caplog.at_level(logging.ERROR):
            _run_send_email(payload)

        assert _saved_attachments(sendemail_mocks.app) == []
        assert any(
            "Attachment ownership check could not resolve" in r.getMessage()
            and "fail closed" in r.getMessage()
            for r in caplog.records
        )

    def test_attachment_matched_by_current_axisrequestid_is_retained(self, sendemail_mocks):
        """FOIMOD-4270 Case A: modern uploads carry the current axisrequestid.

        S3 layout for ministryrequest 760: /JERI/JER-2026-000758/... where
        bcgovcode='JERI' (segment 1) and axisrequestid='JER-2026-000758'
        (segment 2). filenumber ('JERI-2022-75840815') does NOT appear in
        the URL and must not be required to match.
        """
        sendemail_mocks.resolve.return_value = (
            "JERI",
            {"JERI-2022-75840815", "JER-2026-000758"},
        )
        payload = _make_payload([
            # Case A: current axisrequestid — retained.
            {"filename": "ours-axis.pdf",
             "url": "https://bucket/forms/JERI/JER-2026-000758/ours-axis.pdf"},
            # Case B: filenumber — also retained (AXIS-era uploads).
            {"filename": "ours-filenumber.pdf",
             "url": "https://bucket/forms/JERI/JERI-2022-75840815/ours-filenumber.pdf"},
            # Wrong ministry — dropped.
            {"filename": "leaked.pdf",
             "url": "https://bucket/forms/OTHER/JER-2026-000758/leaked.pdf"},
            # Right ministry, wrong request — dropped.
            {"filename": "wrong-request.pdf",
             "url": "https://bucket/forms/JERI/JER-2999-999999/wrong-request.pdf"},
        ])

        _run_send_email(payload, ministryrequestid=760)

        assert sorted(a["filename"] for a in _saved_attachments(sendemail_mocks.app)) == [
            "ours-axis.pdf", "ours-filenumber.pdf",
        ]

    def test_attachment_matched_by_historical_axisrequestid_is_retained(self, sendemail_mocks):
        """FOIMOD-4270 Case C: renumbered mid-life.

        The current row shows axisrequestid='TRA-2026-003230' but older row
        versions carried 'TRA-2025-92783', and S3 keys stamped at upload
        time still reference the old value. _resolve_ownership_coords is
        responsible for surfacing both values via the DISTINCT historical
        query; here we pre-populate the returned set to verify the validator
        accepts a match against the historical value.
        """
        sendemail_mocks.resolve.return_value = (
            "TRAN",
            {
                "TRAN-2022-000123",       # filenumber
                "TRA-2026-003230",        # current axisrequestid
                "TRA-2025-92783",         # historical axisrequestid
            },
        )
        payload = _make_payload([
            # Pre-renumber S3 key — historical axisrequestid.
            {"filename": "pre-renumber.pdf",
             "url": "https://bucket/forms/TRAN/TRA-2025-92783/pre-renumber.pdf"},
            # Post-renumber S3 key — current axisrequestid.
            {"filename": "post-renumber.pdf",
             "url": "https://bucket/forms/TRAN/TRA-2026-003230/post-renumber.pdf"},
        ])

        _run_send_email(payload, ministryrequestid=555)

        assert sorted(a["filename"] for a in _saved_attachments(sendemail_mocks.app)) == [
            "post-renumber.pdf", "pre-renumber.pdf",
        ]


# ---------------------------------------------------------------------------
# Validator: iterable-of-requestnumbers API (FOIMOD-4270 Option B).
# ---------------------------------------------------------------------------

class TestValidateAttachmentOwnershipMultipleRequestNumbers:
    """Option B: validator accepts an iterable of accepted requestnumbers."""

    def test_iterable_of_requestnumbers_matches_any(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "by-filenumber.pdf",
             "url": "https://bucket/forms/MIN/MIN-2022-000001/by-filenumber.pdf"},
            {"filename": "by-axisid.pdf",
             "url": "https://bucket/forms/MIN/MIN-2026-99999/by-axisid.pdf"},
            {"filename": "leaked.pdf",
             "url": "https://bucket/forms/MIN/MIN-2099-111111/leaked.pdf"},
        ]
        result = svc._validate_attachment_ownership(
            attachments, "MIN", {"MIN-2022-000001", "MIN-2026-99999"}
        )
        assert sorted(a["filename"] for a in result) == [
            "by-axisid.pdf", "by-filenumber.pdf",
        ]

    def test_string_requestnumber_still_supported(self):
        """Back-compat: a bare string is treated as a single-value set."""
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ok.pdf",
             "url": "https://bucket/forms/MIN/MIN-2026-00001/ok.pdf"},
        ]
        result = svc._validate_attachment_ownership(
            attachments, "MIN", "MIN-2026-00001"
        )
        assert result == attachments

    @pytest.mark.parametrize("empty_value", [[], set(), None])
    def test_empty_requestnumbers_rejects_everything(self, empty_value):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "a.pdf",
             "url": "https://bucket/forms/MIN/MIN-2026-00001/a.pdf"},
        ]
        assert svc._validate_attachment_ownership(attachments, "MIN", empty_value) == []

    def test_none_values_in_iterable_are_dropped(self):
        svc = communicationwrapperservice()
        attachments = [
            {"filename": "ok.pdf",
             "url": "https://bucket/forms/MIN/MIN-2026-00001/ok.pdf"},
        ]
        result = svc._validate_attachment_ownership(
            attachments, "MIN", [None, "", "MIN-2026-00001"]
        )
        assert result == attachments


# ---------------------------------------------------------------------------
# _resolve_ownership_coords: coordinate resolution for the ownership check.
# ---------------------------------------------------------------------------

def _mk_execute(historical_axisrows=(), bcgov_fallback_row=None):
    """Build a mock db.session.execute that dispatches by SQL text.

    Returns:
      - historical_axisrows for the DISTINCT axisrequestid query,
      - bcgov_fallback_row for the bcgovcode fallback query.
    """
    def _execute(stmt, params):
        result = MagicMock()
        if "DISTINCT axisrequestid" in str(stmt):
            result.fetchall.return_value = list(historical_axisrows)
        else:
            result.fetchone.return_value = bcgov_fallback_row
        return result
    return MagicMock(side_effect=_execute)


def _resolve(ministry_dict, *, execute=None, mid=1):
    """Drive _resolve_ownership_coords with mocked getrequest + db.execute."""
    with patch("request_api.services.communicationwrapperservice.FOIMinistryRequest") as mock_ministry, \
         patch("request_api.models.db.db") as mock_db:
        mock_ministry.getrequest.return_value = ministry_dict
        mock_db.session.execute = execute if execute is not None else _mk_execute()
        return communicationwrapperservice()._resolve_ownership_coords(mid)


class TestResolveOwnershipCoords:
    """FOIMOD-4270 Option B: resolution of (ministrycode, requestnumbers)."""

    def test_resolves_from_schema_dump_with_dotted_bcgovcode(self):
        code, numbers = _resolve(
            {
                "filenumber": "JERI-2022-75840815",
                "axisrequestid": "JER-2026-000758",
                "programarea.bcgovcode": "JERI",
            },
            execute=_mk_execute(
                historical_axisrows=[("JER-2022-00087",), ("JER-2026-000758",)],
            ),
            mid=760,
        )
        assert code == "JERI"
        # current filenumber + current axisrequestid + all historical axisrequestids
        assert numbers == {
            "JERI-2022-75840815",
            "JER-2026-000758",
            "JER-2022-00087",
        }

    def test_falls_back_to_bare_bcgovcode_key(self):
        """Defensive alias: if the schema ever flattens 'programarea.bcgovcode'
        to a bare 'bcgovcode' key, we still pick it up without needing SQL."""
        code, numbers = _resolve(
            {"filenumber": "MIN-2026-00001", "bcgovcode": "MIN"},
        )
        assert code == "MIN"
        assert numbers == {"MIN-2026-00001"}

    def test_fallback_sql_supplies_bcgovcode_when_schema_lacks_it(self):
        # No 'programarea.bcgovcode' / 'bcgovcode' key at all.
        code, numbers = _resolve(
            {"filenumber": "MIN-2026-00001"},
            execute=_mk_execute(bcgov_fallback_row=("min",)),
        )
        assert code == "min"
        assert numbers == {"MIN-2026-00001"}

    def test_returns_empty_when_nothing_resolvable(self):
        code, numbers = _resolve({})
        assert code is None
        assert numbers == set()

    def test_historical_query_failure_does_not_break_resolution(self):
        """If the DISTINCT lookup raises, we fall back to current-row values."""
        code, numbers = _resolve(
            {
                "filenumber": "MIN-2026-00001",
                "axisrequestid": "MIN-2026-99999",
                "programarea.bcgovcode": "MIN",
            },
            execute=MagicMock(side_effect=RuntimeError("boom")),
        )
        assert code == "MIN"
        assert numbers == {"MIN-2026-00001", "MIN-2026-99999"}

    def test_null_historical_rows_are_ignored(self):
        code, numbers = _resolve(
            {"filenumber": "MIN-2026-00001", "programarea.bcgovcode": "MIN"},
            execute=_mk_execute(
                historical_axisrows=[(None,), ("",), ("MIN-2020-000001",)],
            ),
        )
        assert code == "MIN"
        assert numbers == {"MIN-2026-00001", "MIN-2020-000001"}
