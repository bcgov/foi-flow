"""FOIMOD-5517 migration: values, renames and bucket naming (no database)."""

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "migrations/versions/a0134b09838d_FOIMOD_5517_ministry_reorganization.py"
_spec = importlib.util.spec_from_file_location("foimod_5517_migration", _PATH)
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)


def test_replacements():
    assert [(r["old"], r["new"]) for r in migration.REPLACEMENTS] == [("ECS", "EMP"), ("HSG", "LHS"), ("JED", "EDT")]


@pytest.mark.parametrize("old,new,bucket,expected", [
    ("ECS", "EMP", "ecs-dev-e", "emp-dev-e"),
    ("HSG", "LHS", "hsg-prod-e", "lhs-prod-e"),
    ("ECS", "EMP", "ECS-test-e", "emp-test-e"),
])
def test_new_bucket_keeps_the_environment_suffix(old, new, bucket, expected):
    assert migration._new_bucket(old, new, bucket) == expected


def test_unexpected_bucket_name_is_refused():
    with pytest.raises(RuntimeError):
        migration._new_bucket("ECS", "EMP", "energy-records")


def test_follows_the_current_head():
    assert migration.down_revision == "a4e9c7d2f1b6"


def test_renames_are_name_only_for_the_approved_ministries():
    assert set(migration.RENAMES) == {"AGR", "CITZ", "ENV", "PSE", "MSD", "TRAN", "WLR"}
    replaced = {r["old"] for r in migration.REPLACEMENTS}
    assert not replaced & set(migration.RENAMES)
    for old_name, new_name in migration.RENAMES.values():
        assert old_name != new_name
        assert new_name.startswith("Ministry of ")


def test_new_ministry_names_match_the_public_form():
    # Same spelling as bcgov/foi-requests data.json, with Flow's "Ministry of" prefix.
    assert {r["new"]: r["name"] for r in migration.REPLACEMENTS} == {
        "EMP": "Ministry of Energy, Mines and Petroleum Resources",
        "LHS": "Ministry of Local Government, Housing, Sport and Culture",
        "EDT": "Ministry of Economic Development and Tourism",
    }


class _FakeConn:
    """Answers the rename check's name lookups and records the updates."""

    def __init__(self, names):
        self.names = names
        self.updates = []

    def execute(self, statement, params):
        conn = self

        class _Result:
            def scalar(self):
                return conn.names.get(params["c"])

        if str(statement).lstrip().startswith("UPDATE"):
            self.updates.append(params)
        return _Result()


def _current_names():
    return {code: old_name for code, (old_name, _) in migration.RENAMES.items()}


def test_rename_applies_new_names_when_all_ministries_have_their_old_names():
    conn = _FakeConn(_current_names())
    migration._rename(conn)
    assert {u["c"]: u["n"] for u in conn.updates} == {
        code: new_name for code, (_, new_name) in migration.RENAMES.items()
    }


def test_rename_refuses_a_ministry_that_already_has_its_new_name():
    names = _current_names()
    names["AGR"] = migration.RENAMES["AGR"][1]
    conn = _FakeConn(names)
    with pytest.raises(RuntimeError, match="ministry AGR is named"):
        migration._rename(conn)
    assert conn.updates == []


def test_new_bucket_does_not_reuse_the_old_ministrys_storage_keys():
    # The new bucket gets its own storage user; its keys are filled in through the credential process.
    sql = migration.EMPTY_CREDENTIALS_SQL
    assert "jsonb_build_object('s3accesskey', '', 's3secretkey', '')" in sql
    assert sql.startswith("(attributes::jsonb ||")
