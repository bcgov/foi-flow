"""FOIMOD-5515 migration: values, renames and bucket naming (no database)."""

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "migrations/versions/a0134b09838d_FOIMOD_5515_ministry_reorganization.py"
_spec = importlib.util.spec_from_file_location("foimod_5515_migration", _PATH)
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
