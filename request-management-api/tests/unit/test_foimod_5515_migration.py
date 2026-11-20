"""FOIMOD-5515 migration: values and bucket naming (no database)."""

import importlib.util
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[2] / "migrations/versions/a0134b09838d_FOIMOD_5515_emp_lhs_ministries.py"
_spec = importlib.util.spec_from_file_location("foimod_5515_migration", _PATH)
migration = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migration)


def test_replacements():
    assert [(r["old"], r["new"]) for r in migration.REPLACEMENTS] == [("ECS", "EMP"), ("HSG", "LHS")]


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
