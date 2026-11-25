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
    # FOIMOD-5517: EMP replaces ECS, LHS replaces HSG and EDT replaces JED. The old ministries'
    # staff work on the new ministries' requests without being copied into the new groups.
    "EMP Ministry Team": ("ECS Ministry Team","EMLI Ministry Team",),
    "LHS Ministry Team": ("HSG Ministry Team","MUNI Ministry Team",),
    "EDT Ministry Team": ("JED Ministry Team","JERI Ministry Team",),
    "ECC Ministry Team": ("EDU Ministry Team",),
    "PSE Ministry Team": ("AEST Ministry Team",),
    "CAS Ministry Team": ("BRD Ministry Team",),
    "HTH Ministry Team": ("MMHA Ministry Team",),
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
