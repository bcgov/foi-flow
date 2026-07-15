import logging
from unittest.mock import patch, MagicMock


def test_send_logs_email_metadata(caplog):
    from request_api.services.email.senderservice import senderservice
    fake_download = MagicMock()
    fake_download.content = b"file-bytes"
    with patch("request_api.services.email.senderservice.smtplib.SMTP") as smtp_ctx, \
         patch("request_api.services.email.senderservice.storageservice") as storage, \
         patch("request_api.services.email.senderservice.embeddedimagehandler") as eimg:
        smtp_ctx.return_value.__enter__.return_value.sendmail.return_value = {}
        storage.return_value.download.return_value = fake_download
        eimg.return_value.formatembeddedimage.return_value = ("hi", [])
        with caplog.at_level(logging.INFO, logger="request_api.services.email.senderservice"):
            senderservice().send(
                subject="Test subject",
                content="hi",
                _messageattachmentlist=[{"filename": "a.pdf", "url": "u"}],
                emails=["to@x.com"],
                ccemails=["cc@x.com"],
            )
    assert any(
        "Sending email" in r.getMessage()
        and "Test subject" in r.getMessage()
        and "a.pdf" in r.getMessage()
        for r in caplog.records
    )
