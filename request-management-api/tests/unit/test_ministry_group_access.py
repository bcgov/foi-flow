"""Ministry group access grants: members of one ministry group also act on another."""

from unittest.mock import patch

import pytest
from flask import Flask
from jose import jwt as josejwt

from request_api.auth import AuthHelper
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.utils.enums import MinistryTeamWithKeycloackGroup
from request_api.utils.ministrygroupaccess import (
    MINISTRY_GROUP_ACCESS_GRANTS,
    grantinggroups,
    withgrantedgroups,
)

EDU = "EDU Ministry Team"
FAKE = "FAKE Ministry Team"
HTH = "HTH Ministry Team"
GRANTS = {EDU: (FAKE,)}


def test_source_group_members_get_the_granted_group():
    assert withgrantedgroups([EDU], GRANTS) == [EDU, FAKE]


def test_grant_is_one_way():
    assert withgrantedgroups([FAKE], GRANTS) == [FAKE]


def test_member_of_both_groups_has_no_duplicates():
    assert withgrantedgroups([EDU, FAKE], GRANTS) == [EDU, FAKE]


def test_other_groups_are_unchanged():
    assert withgrantedgroups([HTH, "Intake Team"], GRANTS) == [HTH, "Intake Team"]


def test_granting_groups_lists_the_sources():
    assert grantinggroups(FAKE, GRANTS) == [EDU]
    assert grantinggroups(EDU, GRANTS) == []


def test_configured_grants_use_known_ministry_groups():
    known = set(MinistryTeamWithKeycloackGroup.list())
    for source, granted in MINISTRY_GROUP_ACCESS_GRANTS.items():
        assert source in known
        assert set(granted) <= known
        assert source not in granted


def _token(groups):
    return josejwt.encode({"groups": groups}, "unit-test-key", algorithm="HS256")


@pytest.fixture
def as_user():
    app = Flask(__name__)

    def _as_user(groups):
        headers = {"Authorization": f"Bearer {_token(groups)}"}
        return app.test_request_context(headers=headers)

    return _as_user


@patch.dict(MINISTRY_GROUP_ACCESS_GRANTS, GRANTS, clear=True)
def test_edu_only_user_is_treated_as_fake_member(as_user):
    with as_user(["/" + EDU]):
        assert AuthHelper.getusertype() == "ministry"
        assert sorted(AuthHelper.getministrygroups()) == [EDU, FAKE]


@patch.dict(MINISTRY_GROUP_ACCESS_GRANTS, GRANTS, clear=True)
def test_fake_only_user_does_not_get_edu(as_user):
    with as_user(["/" + FAKE]):
        assert AuthHelper.getusertype() == "ministry"
        assert AuthHelper.getministrygroups() == [FAKE]


def _member(username, lastname):
    return {"username": username, "lastname": lastname}


@patch.dict(MINISTRY_GROUP_ACCESS_GRANTS, GRANTS, clear=True)
def test_granted_group_members_include_source_group_members():
    service = KeycloakAdminService()
    allgroups = [{"id": "edu-id", "name": EDU}, {"id": "fake-id", "name": FAKE}]
    edu_members = [_member("a@idir", "Adams"), _member("shared@idir", "Shared")]
    groups = [{"id": "fake-id", "name": FAKE, "members": [_member("shared@idir", "Shared"), _member("z@idir", "Zed")]}]
    with patch.object(KeycloakAdminService, "getallgroups", return_value=allgroups), patch.object(
        KeycloakAdminService, "getgroupmembersbyid", return_value=edu_members
    ) as members_by_id:
        result = service.addgrantedmembers(groups)
    members_by_id.assert_called_once_with("edu-id")
    assert [m["username"] for m in result[0]["members"]] == ["a@idir", "shared@idir", "z@idir"]


@patch.dict(MINISTRY_GROUP_ACCESS_GRANTS, GRANTS, clear=True)
def test_groups_without_grants_are_not_changed():
    service = KeycloakAdminService()
    groups = [{"id": "edu-id", "name": EDU, "members": [_member("a@idir", "Adams")]}]
    with patch.object(KeycloakAdminService, "getallgroups") as allgroups:
        result = service.addgrantedmembers(groups)
    allgroups.assert_not_called()
    assert result[0]["members"] == [_member("a@idir", "Adams")]


@pytest.mark.parametrize("old,new", [("ECS", "EMP"), ("HSG", "LHS"), ("JED", "EDT")])
def test_foimod_5515_old_ministry_staff_get_the_new_ministry(old, new):
    old_group, new_group = f"{old} Ministry Team", f"{new} Ministry Team"
    assert new_group in MINISTRY_GROUP_ACCESS_GRANTS[old_group]
    assert withgrantedgroups([old_group]) == [old_group, new_group]
    assert withgrantedgroups([new_group]) == [new_group]
