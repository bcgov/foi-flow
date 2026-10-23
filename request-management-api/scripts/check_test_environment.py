"""Fail closed before tests can import the API or run database migrations."""

from collections.abc import Mapping
import os
from urllib.parse import urlparse


def validate_test_environment(environ: Mapping[str, str]) -> None:
    """Require the dedicated Compose peers, including an explicit test DB."""
    if environ.get("FLASK_ENV") != "testing":
        raise ValueError("FLASK_ENV must explicitly be testing")
    if environ.get('PYTHON_DOTENV_DISABLED') != '1':
        raise ValueError('PYTHON_DOTENV_DISABLED must be 1 before API imports')
    if environ.get('OSS_S3_HOST') != 'storage:8333':
        raise ValueError('OSS_S3_HOST must use the dedicated storage peer')
    endpoints = {
        "DATABASE_TEST_URL": ("postgres", {"postgresql", "postgresql+psycopg2"}, 5432),
        "REDIS_URL": ("redis", {"redis"}, 6379),
        "CACHE_REDISURL": ("redis", {"redis"}, 6379),
        "S3_ENDPOINT_URL": ("storage", {"http", "https"}, 8333),
        "JWT_OIDC_ISSUER": ("oidc", {"http"}, 8080),
        "JWT_OIDC_JWKS_URI": ("oidc", {"http"}, 8080),
        "JWT_OIDC_WELL_KNOWN_CONFIG": ("oidc", {"http"}, 8080),
        "KEYCLOAK_ADMIN_HOST": ("oidc", {"http"}, 8080),
    }
    for name, (host, schemes, port) in endpoints.items():
        value = urlparse(environ.get(name, ""))
        if value.hostname != host or value.scheme not in schemes or value.port != port:
            raise ValueError(f"{name} must use its dedicated Compose peer")
        if value.query or value.fragment:
            raise ValueError(f"{name} cannot contain endpoint overrides")
        if name == "DATABASE_TEST_URL" and not value.path.startswith("/foi_upgrade_test"):
            raise ValueError("Database name must start with foi_upgrade_test")
    for prefix in ("DATABASE", "DATABASE_TEST"):
        if environ.get(f"{prefix}_HOST", "postgres") != "postgres":
            raise ValueError(f"{prefix}_HOST must be postgres")
        if not environ.get(f"{prefix}_NAME", "foi_upgrade_test").startswith("foi_upgrade_test"):
            raise ValueError(f"{prefix}_NAME must name a test database")
        if environ.get(f"{prefix}_PORT", "5432") != "5432":
            raise ValueError(f"{prefix}_PORT must be 5432")
    for name in ("SOCKETIO_REDIS_HOST", "PUBLICATION_REDIS_HOST", "FOI_REQUESTQUEUE_REDISHOST", "EVENT_QUEUE_HOST"):
        if environ.get(name, "redis") != "redis":
            raise ValueError(f"{name} must be redis")
    if environ.get('EVENT_QUEUE_PORT', '6379') != '6379':
        raise ValueError('EVENT_QUEUE_PORT must be 6379')


if __name__ == "__main__":
    validate_test_environment(os.environ)
