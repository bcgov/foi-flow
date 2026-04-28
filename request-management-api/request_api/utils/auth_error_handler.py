"""Handlers for authentication errors."""

from flask import jsonify, request


def log_auth_error(error, logger):
    """Log authentication errors at the appropriate severity."""
    error_body = getattr(error, "error", {}) or {}
    error_code = error_body.get("code")
    description = error_body.get("description")

    if error_code == "token_expired":
        logger.warning(
            "JWT token expired for %s %s: %s",
            request.method,
            request.path,
            description,
        )
    else:
        logger.error(
            "JWT authentication failed for %s %s: %s",
            request.method,
            request.path,
            error_body,
            exc_info=True,
        )


def auth_error_response(error, logger):
    """Build the Flask error response for authentication errors."""
    error_body = getattr(error, "error", {}) or {}
    status_code = getattr(error, "status_code", 401)

    log_auth_error(error, logger)

    return jsonify(error_body), status_code


def auth_error_restx_response(error, logger):
    """Build the Flask-RESTX error response for authentication errors."""
    error_body = getattr(error, "error", {}) or {}
    status_code = getattr(error, "status_code", 401)

    log_auth_error(error, logger)

    return error_body, status_code
