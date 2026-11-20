"""MinistryTeamWithKeycloackGroup: bcgovcode -> Keycloak ministry group mapping."""

from request_api.utils.enums import MinistryTeamWithKeycloackGroup
from request_api.utils.util import getrequiredmemberships


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


def test_foimod_5515_new_ministries_have_their_own_groups():
    assert MinistryTeamWithKeycloackGroup["EMP"].value == "EMP Ministry Team"
    assert MinistryTeamWithKeycloackGroup["LHS"].value == "LHS Ministry Team"


def test_foimod_5515_replaced_ministries_keep_their_groups():
    # Their existing requests still use these groups.
    assert MinistryTeamWithKeycloackGroup["ECS"].value == "ECS Ministry Team"
    assert MinistryTeamWithKeycloackGroup["HSG"].value == "HSG Ministry Team"
