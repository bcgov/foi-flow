"""Ministry group access grants.

Members of a key group also get access to the listed ministry groups, as if they were
members of them. Keycloak and the user's token are not changed. Used when a new ministry
is created with its own group, and the staff of an existing ministry must also work on its
requests without being copied into the new group.

Grants are one way: members of the key group get the listed groups, not the reverse.
Removing an entry ends the shared access; requests keep their own ministry group, so no
data changes are needed.
"""

MINISTRY_GROUP_ACCESS_GRANTS = {
    # FOIMOD-5515: EMP replaces ECS and LHS replaces HSG. The old ministries' staff work on the
    # new ministries' requests without being copied into the new groups.
    "ECS Ministry Team": ("EMP Ministry Team",),
    "HSG Ministry Team": ("LHS Ministry Team",),
    # Local reorganization testing only: remove before merging to main.
    "EDU Ministry Team": ("FAKE Ministry Team",),
}


def withgrantedgroups(usergroups, grants=None):
    """Return the user's groups plus every group granted by them, without duplicates."""
    grants = MINISTRY_GROUP_ACCESS_GRANTS if grants is None else grants
    groups = list(usergroups)
    for usergroup in usergroups:
        for granted in grants.get(usergroup, ()):
            if granted not in groups:
                groups.append(granted)
    return groups


def grantinggroups(groupname, grants=None):
    """Return the groups whose members are granted access to ``groupname``."""
    grants = MINISTRY_GROUP_ACCESS_GRANTS if grants is None else grants
    return [source for source, granted in grants.items() if groupname in granted]
