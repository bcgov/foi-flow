"""MinistryTeamWithKeycloackGroup: bcgovcode -> Keycloak ministry group mapping."""

import pytest

from request_api.utils.enums import MinistryTeamWithKeycloackGroup
from request_api.utils.util import getrequiredmemberships


def _aliases():
    """Codes mapped onto another ministry's group (Enum members with a repeated value)."""
    return [
        (name, member)
        for name, member in MinistryTeamWithKeycloackGroup.__members__.items()
        if member.name != name
    ]


def test_fake_ministry_maps_to_its_own_group():
    assert MinistryTeamWithKeycloackGroup["FAKE"].value == "FAKE Ministry Team"
    assert "FAKE Ministry Team" in MinistryTeamWithKeycloackGroup.list()


def test_fake_ministry_group_is_a_required_membership():
    assert "FAKE Ministry Team" in getrequiredmemberships().split(",")


def test_canonical_groups_follow_naming_convention():
    for member in MinistryTeamWithKeycloackGroup:
        assert member.value == f"{member.name} Ministry Team"


def test_group_list_has_no_duplicates():
    groups = MinistryTeamWithKeycloackGroup.list()
    assert len(groups) == len(set(groups))


@pytest.mark.parametrize("code,canonical", _aliases() or [pytest.param(None, None, marks=pytest.mark.skip(reason="no aliases defined"))])
def test_alias_resolves_to_existing_ministry_group(code, canonical):
    """A temporary NEWCODE -> OLDCODE alias must give the old group and add no new group."""
    assert MinistryTeamWithKeycloackGroup[code].value == canonical.value
    assert canonical.value in MinistryTeamWithKeycloackGroup.list()
    assert code not in [m.name for m in MinistryTeamWithKeycloackGroup]
