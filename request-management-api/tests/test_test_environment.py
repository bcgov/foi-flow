"""The test harness must refuse shared services before importing the API."""

import importlib.util
from pathlib import Path

import pytest


def validate(environ):
    path = Path(__file__).parents[1] / "scripts" / "check_test_environment.py"
    assert path.is_file(), "test environment guard is missing"
    spec = importlib.util.spec_from_file_location("test_environment_guard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate_test_environment(environ)


@pytest.fixture
def isolated_env():
    return {
        "FLASK_ENV": "testing",
        "PYTHON_DOTENV_DISABLED": "1",
        "DATABASE_TEST_URL": "postgresql://postgres:fake@postgres:5432/foi_upgrade_test",
        "REDIS_URL": "redis://redis:6379/0",
        "CACHE_REDISURL": "redis://redis:6379/1",
        "S3_ENDPOINT_URL": "http://storage:8333",
        "OSS_S3_HOST": "storage:8333",
        "EVENT_QUEUE_HOST": "redis",
        "JWT_OIDC_ISSUER": "http://oidc:8080/realms/test",
        "JWT_OIDC_JWKS_URI": "http://oidc:8080/realms/test/certs",
        "JWT_OIDC_WELL_KNOWN_CONFIG": "http://oidc:8080/realms/test/.well-known/openid-configuration",
        "KEYCLOAK_ADMIN_HOST": "http://oidc:8080",
    }


def test_explicit_disposable_peers_are_accepted(isolated_env):
    validate(isolated_env)


@pytest.mark.parametrize("key", ["FLASK_ENV", "DATABASE_TEST_URL", "REDIS_URL", "S3_ENDPOINT_URL"])
def test_missing_test_configuration_is_rejected(isolated_env, key):
    isolated_env.pop(key)
    with pytest.raises(ValueError):
        validate(isolated_env)


@pytest.mark.parametrize("url", [
    "postgresql://postgres:fake@shared-db:5432/foi_upgrade_test",
    "postgresql://postgres:fake@postgres:5432/production",
    "postgresql://postgres:fake@localhost:5432/foi_upgrade_test",
    "postgresql://postgres:fake@postgres.evil:5432/foi_upgrade_test",
])
def test_shared_or_non_test_database_is_rejected(isolated_env, url):
    isolated_env["DATABASE_TEST_URL"] = url
    with pytest.raises(ValueError):
        validate(isolated_env)


@pytest.mark.parametrize("key,url", [
    ("REDIS_URL", "redis://shared:6379/0"),
    ("CACHE_REDISURL", "redis://shared:6379/0"),
    ("S3_ENDPOINT_URL", "https://real-bucket.example"),
    ("JWT_OIDC_ISSUER", "https://real-keycloak.example/realms/test"),
    ("JWT_OIDC_JWKS_URI", "https://real-keycloak.example/certs"),
    ("JWT_OIDC_WELL_KNOWN_CONFIG", "https://real-keycloak.example/config"),
    ("KEYCLOAK_ADMIN_HOST", "https://real-keycloak.example"),
])
def test_shared_redis_storage_or_identity_is_rejected(isolated_env, key, url):
    isolated_env[key] = url
    with pytest.raises(ValueError):
        validate(isolated_env)


def test_guard_rejects_mismatched_application_database(isolated_env):
    isolated_env["DATABASE_HOST"] = "shared-db"
    with pytest.raises(ValueError):
        validate(isolated_env)


@pytest.mark.parametrize("key", ["DATABASE_PORT", "DATABASE_TEST_PORT", "SOCKETIO_REDIS_HOST", "PUBLICATION_REDIS_HOST"])
def test_guard_rejects_alternate_application_peer(isolated_env, key):
    isolated_env[key] = "15432" if key.endswith("PORT") else "shared-redis"
    with pytest.raises(ValueError):
        validate(isolated_env)


@pytest.mark.parametrize('value', [None, '', '0'])
def test_guard_requires_dotenv_disabled_before_import(isolated_env, value):
    if value is None:
        isolated_env.pop('PYTHON_DOTENV_DISABLED')
    else:
        isolated_env['PYTHON_DOTENV_DISABLED'] = value
    with pytest.raises(ValueError):
        validate(isolated_env)


@pytest.mark.parametrize('key,value', [
    ('OSS_S3_HOST', 'real-storage.example'),
    ('EVENT_QUEUE_HOST', 'shared-redis'),
])
def test_guard_validates_actual_application_storage_and_stream_hosts(isolated_env, key, value):
    isolated_env[key] = value
    with pytest.raises(ValueError):
        validate(isolated_env)
