import logging
from unittest.mock import patch, MagicMock

import pytest

from request_api.services.communicationwrapperservice import communicationwrapperservice


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


class TestSendEmailStripsForeignAttachments:
    @patch("request_api.services.communicationwrapperservice.AuthHelper")
    @patch("request_api.services.communicationwrapperservice.communicationemailservice")
    @patch("request_api.services.communicationwrapperservice.applicantcorrespondenceservice")
    @patch("request_api.services.communicationwrapperservice.FOIMinistryRequest")
    def test_foreign_attachment_never_saved_or_sent(
        self, mock_ministry, mock_appservice, mock_emailservice, mock_auth
    ):
        # Arrange — request belongs to MIN / MIN-2026-00001
        mock_auth.getuserid.return_value = "tester"
        mock_ministry.getrequest.return_value = {
            "filenumber": "MIN-2026-00001",
            "bcgovcode": "MIN",
        }
        save_result = MagicMock(success=True, identifier=42, message="ok")
        mock_appservice.return_value.saveapplicantcorrespondencelog.return_value = save_result
        # gettemplatebyid returns None for templatename branch, and later the
        # non-fee path calls it again — return a template-like object regardless.
        tpl = MagicMock()
        tpl.name = "GENERIC"
        mock_appservice.return_value.gettemplatebyid.return_value = tpl
        mock_emailservice.return_value.send.return_value = {
            "success": True, "from_email": "noreply@gov.bc.ca"
        }

        payload = {
            "correspondencemessagejson": '{"body":"hi"}',
            "attributes": [{}],
            "correspondencesubject": "S",
            "templatename": "GENERIC",
            "templateid": None,
            "emails": ["a@x.com"],
            "attachments": [
                {"filename": "ours.pdf",
                 "url": "https://bucket/forms/MIN/MIN-2026-00001/ours.pdf"},
                {"filename": "leaked.pdf",
                 "url": "https://bucket/forms/OTHER/OTHER-2026-99999/leaked.pdf"},
            ],
        }

        # Act
        communicationwrapperservice().send_email(
            requestid=1, rawrequestid=None, ministryrequestid=99,
            applicantcorrespondencelog=payload,
        )

        # Assert — the saved log received only the owned attachment
        saved_call = mock_appservice.return_value.saveapplicantcorrespondencelog.call_args
        saved_log = saved_call.args[2] if len(saved_call.args) >= 3 else saved_call.kwargs["applicantcorrespondencelog"]
        assert len(saved_log["attachments"]) == 1
        assert saved_log["attachments"][0]["filename"] == "ours.pdf"

        # Assert — the email service also received only the owned attachment
        sent_call = mock_emailservice.return_value.send.call_args
        sent_log = sent_call.args[1]
        assert len(sent_log["attachments"]) == 1
        assert sent_log["attachments"][0]["filename"] == "ours.pdf"
