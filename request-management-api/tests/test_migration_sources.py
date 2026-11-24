"""Check that every Alembic revision compiles cleanly on the running Python."""

from pathlib import Path
import warnings

import pytest


VERSIONS_DIR = Path(__file__).resolve().parents[1] / "migrations" / "versions"


@pytest.mark.parametrize("revision", sorted(VERSIONS_DIR.glob("*.py")), ids=lambda path: path.name)
def test_revision_compiles_without_warnings(revision):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        compile(revision.read_bytes(), str(revision), "exec")
