"""Extract required scalar versions at service boundaries."""

from request_api.exceptions import BusinessException, CustomException


def require_request_version(version_row) -> int:
    """Return the version from a lookup row, rejecting an unknown request."""
    if version_row is None:
        raise BusinessException(CustomException(
            "Request version not found", 404, "REQUEST_VERSION_NOT_FOUND"
        ))
    return version_row[0]
