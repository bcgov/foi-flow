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


def test_atomic_upsert_uses_postgresql_conflict_handling():
    from sqlalchemy.dialects import postgresql

    from request_api.models.FOIUserPreferences import FOIUserPreference

    statement = FOIUserPreference._build_upsert_statement(
        "test.user@idir",
        {"dashboard": {"queue": {"pageSize": 50}}},
        1
    )

    sql = str(statement.compile(dialect=postgresql.dialect()))

    assert 'INSERT INTO "FOIUserPreferences"' in sql
    assert 'ON CONFLICT (userid) DO UPDATE' in sql
    assert 'preferences = excluded.preferences' in sql
    assert 'schema_version = excluded.schema_version' in sql


def test_atomic_upsert_executes_before_reading_saved_row():
    from request_api.models.FOIUserPreferences import FOIUserPreference
    from request_api.models.db import db

    saved_preference = Mock()

    with patch.object(db.session, "execute") as execute, \
         patch.object(db.session, "commit") as commit, \
         patch.object(FOIUserPreference, "getbyuserid", return_value=saved_preference) as lookup:
        result = FOIUserPreference.upsert("test.user@idir", {"test": True}, 1)

    assert result is saved_preference
    execute.assert_called_once()
    commit.assert_called_once()
    lookup.assert_called_once_with("test.user@idir")
