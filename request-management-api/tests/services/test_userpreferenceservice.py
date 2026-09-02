from unittest.mock import Mock, patch

import pytest

from request_api.services.userpreferenceservice import (
    CURRENT_SCHEMA_VERSION,
    userpreferenceservice,
)


def test_get_preferences_returns_default_when_user_has_no_record():
    with patch(
        "request_api.services.userpreferenceservice."
        "FOIUserPreference.getbyuserid",
        return_value=None
    ):
        result = userpreferenceservice().getpreferences(
            "test.user@idir"
        )

    assert result == {
        "schemaVersion": CURRENT_SCHEMA_VERSION,
        "preferences": {}
    }


def test_get_preferences_returns_saved_document():
    preference = Mock()

    preference.asdict.return_value = {
        "schemaVersion": 1,
        "preferences": {
            "dashboard": {
                "queue": {
                    "pageSize": 50
                }
            }
        }
    }

    with patch(
        "request_api.services.userpreferenceservice."
        "FOIUserPreference.getbyuserid",
        return_value=preference
    ):
        result = userpreferenceservice().getpreferences(
            "test.user@idir"
        )

    assert (
        result["preferences"]["dashboard"]["queue"]["pageSize"]
        == 50
    )


def test_save_preferences_uses_authenticated_user_id():
    saved_preference = Mock()

    saved_preference.asdict.return_value = {
        "schemaVersion": 1,
        "preferences": {
            "dashboard": {
                "queue": {
                    "pageSize": 100
                }
            }
        }
    }

    payload = {
        "schemaVersion": 1,
        "preferences": {
            "dashboard": {
                "queue": {
                    "pageSize": 100
                }
            }
        }
    }

    with patch(
        "request_api.services.userpreferenceservice."
        "FOIUserPreference.upsert",
        return_value=saved_preference
    ) as upsert:
        result = userpreferenceservice().savepreferences(
            "test.user@idir",
            payload
        )

    upsert.assert_called_once_with(
        "test.user@idir",
        payload["preferences"],
        1
    )

    assert (
        result["preferences"]["dashboard"]["queue"]["pageSize"]
        == 100
    )


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        "invalid",
        {
            "schemaVersion": "1",
            "preferences": {}
        },
        {
            "schemaVersion": True,
            "preferences": {}
        },
        {
            "schemaVersion": 2,
            "preferences": {}
        },
        {
            "schemaVersion": 1,
            "preferences": []
        },
    ]
)
def test_save_preferences_rejects_invalid_payload(payload):
    with pytest.raises(ValueError):
        userpreferenceservice().savepreferences(
            "test.user@idir",
            payload
        )


def test_preferences_cannot_be_saved_without_authenticated_user():
    with pytest.raises(ValueError):
        userpreferenceservice().savepreferences(
            None,
            {
                "schemaVersion": 1,
                "preferences": {}
            }
        )
