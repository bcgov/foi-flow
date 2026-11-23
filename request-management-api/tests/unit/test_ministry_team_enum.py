"""MinistryTeamWithKeycloackGroup: bcgovcode -> Keycloak ministry group mapping."""

from request_api.utils.enums import MinistryTeamWithKeycloackGroup
from request_api.utils.util import getrequiredmemberships


def test_new_ministry_groups_are_required_memberships():
    memberships = getrequiredmemberships().split(",")
    for group in ("EMP Ministry Team", "LHS Ministry Team", "EDT Ministry Team"):
        assert group in memberships


def test_canonical_groups_follow_naming_convention():
    for member in MinistryTeamWithKeycloackGroup:
        assert member.value == f"{member.name} Ministry Team"


def test_group_list_has_no_duplicates():
    groups = MinistryTeamWithKeycloackGroup.list()
    assert len(groups) == len(set(groups))


def test_foimod_5517_new_ministries_have_their_own_groups():
    assert MinistryTeamWithKeycloackGroup["EMP"].value == "EMP Ministry Team"
    assert MinistryTeamWithKeycloackGroup["LHS"].value == "LHS Ministry Team"
    assert MinistryTeamWithKeycloackGroup["EDT"].value == "EDT Ministry Team"


def test_foimod_5517_replaced_ministries_keep_their_groups():
    # Their existing requests still use these groups.
    assert MinistryTeamWithKeycloackGroup["ECS"].value == "ECS Ministry Team"
    assert MinistryTeamWithKeycloackGroup["HSG"].value == "HSG Ministry Team"
    assert MinistryTeamWithKeycloackGroup["JED"].value == "JED Ministry Team"
