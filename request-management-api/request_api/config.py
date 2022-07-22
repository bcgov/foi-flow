# Copyright © 2021 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""All of the configuration for the service is captured here.

All items are loaded,
or have Constants defined here that are loaded into the Flask configuration.
All modules and lookups get their configuration from the Flask config,
rather than reading environment variables directly or by accessing this configuration directly.
"""

import os
import sys

from dotenv import find_dotenv, load_dotenv


# this will load all the envars from a .env file located in the project root (api)
load_dotenv(find_dotenv())

CONFIGURATION = {
    'development': 'request_api.config.DevConfig',
    'testing': 'request_api.config.TestConfig',
    'production': 'request_api.config.ProdConfig',
    'default': 'request_api.config.ProdConfig'
}


def get_named_config(config_name: str = 'production'):
    """Return the configuration object based on the name.

    :raise: KeyError: if an unknown configuration is requested
    """
    if config_name in ['production', 'staging', 'default']:
        config = ProdConfig()
    elif config_name == 'testing':
        config = TestConfig()
    elif config_name == 'development':
        config = DevConfig()
    else:
        raise KeyError("Unknown configuration '{config_name}'")
    return config


class _Config():  # pylint: disable=too-few-public-methods
    """Base class configuration that should set reasonable defaults for all the other configurations."""

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = 'a secret'

    TESTING = False
    DEBUG = False

    ALEMBIC_INI = 'migrations/alembic.ini'
    # Config to skip migrations when alembic migrate is used
    SKIPPED_MIGRATIONS = ['authorizations_view']

    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_USERNAME', '')
    DB_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DB_NAME = os.getenv('DATABASE_NAME', '')
    DB_HOST = os.getenv('DATABASE_HOST', '')
    DB_PORT = os.getenv('DATABASE_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        name=DB_NAME,
    )
    #Engine configurations
    pool_size = int(os.getenv('SQLALCHEMY_POOL_SIZE', '9'))
    max_overflow = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', '18'))

    pool_timeout_string = os.getenv('SQLALCHEMY_POOL_TIMEOUT', '')
    connect_timeout_string = os.getenv('SQLALCHEMY_CONNECT_TIMEOUT', '')
    pool_pre_ping = (os.getenv('SQLALCHEMY_POOL_PRE_PING', 'False')).upper() == "TRUE"
    db_sql_echo = (os.getenv('SQLALCHEMY_ECHO', 'False')).upper() == "TRUE"
    #  Try to set some options to avoid long delays.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': pool_size,
        'max_overflow': max_overflow,
        'pool_pre_ping': pool_pre_ping
    }

    if pool_timeout_string != "":
        pool_timeout = int(pool_timeout_string)
        SQLALCHEMY_ENGINE_OPTIONS['pool_timeout'] = pool_timeout
    
    if connect_timeout_string != "":
        connect_timeout_int = int(connect_timeout_string)
        SQLALCHEMY_ENGINE_OPTIONS['connect_args'] = {'connect_timeout': connect_timeout_int}

    print(SQLALCHEMY_ENGINE_OPTIONS)
    #Logging echo settings
    SQLALCHEMY_ECHO = db_sql_echo 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    print('SQLAlchemy URL (base): {}'.format(SQLALCHEMY_DATABASE_URI))

    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv('JWT_OIDC_WELL_KNOWN_CONFIG')
    JWT_OIDC_ALGORITHMS = os.getenv('JWT_OIDC_ALGORITHMS')
    JWT_OIDC_JWKS_URI = os.getenv('JWT_OIDC_JWKS_URI')
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')
    JWT_OIDC_AUDIENCE = os.getenv('JWT_OIDC_AUDIENCE')
    JWT_OIDC_CLIENT_SECRET = os.getenv('JWT_OIDC_CLIENT_SECRET')
    JWT_OIDC_CACHING_ENABLED = os.getenv('JWT_OIDC_CACHING_ENABLED')
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv('JWT_OIDC_JWKS_CACHE_TIMEOUT'))
    except ValueError:  # pylint:disable=bare-except # noqa: B901, E722
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300

    
    # email
    MAIL_FROM_ID = os.getenv('MAIL_FROM_ID')

    # Fees
    LEGISLATIVE_TIMEZONE = 'America/Vancouver'
    FOI_WEB_PAY_URL = os.getenv('FOI_WEB_PAY_URL')
    FOI_FFA_URL = os.getenv('FOI_FFA_URL')
    PAYBC_REF_NUMBER = os.getenv('PAYBC_REF_NUMBER')
    PAYBC_PORTAL_URL = os.getenv('PAYBC_PORTAL_URL')
    PAYBC_TXN_PREFIX = os.getenv('PAYBC_TXN_PREFIX', 'FOI')
    PAYBC_API_KEY = os.getenv('PAYBC_API_KEY')

    PAYBC_API_BASE_URL = os.getenv('PAYBC_API_BASE_URL')
    PAYBC_API_CLIENT = os.getenv('PAYBC_API_CLIENT')
    PAYBC_API_SECRET = os.getenv('PAYBC_API_SECRET')
    CONNECT_TIMEOUT = os.getenv('CONNECT_TIMEOUT', 60)

    # CDOGS
    CDOGS_ACCESS_TOKEN = os.getenv('CDOGS_ACCESS_TOKEN')
    CDOGS_BASE_URL = os.getenv('CDOGS_BASE_URL')
    CDOGS_SERVICE_CLIENT = os.getenv('CDOGS_SERVICE_CLIENT')
    CDOGS_SERVICE_CLIENT_SECRET = os.getenv('CDOGS_SERVICE_CLIENT_SECRET')
    CDOGS_TOKEN_URL = os.getenv('CDOGS_TOKEN_URL')

    


class DevConfig(_Config):  # pylint: disable=too-few-public-methods
    """Dev Config."""

    TESTING = False
    DEBUG = True


class TestConfig(_Config):  # pylint: disable=too-few-public-methods
    """In support of testing only.used by the py.test suite."""

    DEBUG = True
    TESTING = True
    # POSTGRESQL
    DB_USER = os.getenv('DATABASE_TEST_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DATABASE_TEST_PASSWORD', 'postgres')
    DB_NAME = os.getenv('DATABASE_TEST_NAME', 'postgres')
    DB_HOST = os.getenv('DATABASE_TEST_HOST', 'localhost')
    DB_PORT = os.getenv('DATABASE_TEST_PORT', '5432')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL',
                                        'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
                                            user=DB_USER,
                                            password=DB_PASSWORD,
                                            host=DB_HOST,
                                            port=int(DB_PORT),
                                            name=DB_NAME,
                                        ))
    
    print('SQLAlchemy URL (Test): {}'.format(SQLALCHEMY_DATABASE_URI))
    
    # JWT_OIDC Settings
    JWT_OIDC_WELL_KNOWN_CONFIG = os.getenv('JWT_OIDC_WELL_KNOWN_CONFIG')
    JWT_OIDC_ALGORITHMS = os.getenv('JWT_OIDC_ALGORITHMS')
    JWT_OIDC_JWKS_URI = os.getenv('JWT_OIDC_JWKS_URI')
    JWT_OIDC_ISSUER = os.getenv('JWT_OIDC_ISSUER')
    JWT_OIDC_AUDIENCE = os.getenv('JWT_OIDC_AUDIENCE')
    JWT_OIDC_CLIENT_SECRET = os.getenv('JWT_OIDC_CLIENT_SECRET')
    JWT_OIDC_CACHING_ENABLED = os.getenv('JWT_OIDC_CACHING_ENABLED')
    try:
        JWT_OIDC_JWKS_CACHE_TIMEOUT = int(os.getenv('JWT_OIDC_JWKS_CACHE_TIMEOUT'))
    except ValueError:  # pylint:disable=bare-except # noqa: B901, E722
        JWT_OIDC_JWKS_CACHE_TIMEOUT = 300
    
class ProdConfig(_Config):  # pylint: disable=too-few-public-methods
    """Production environment configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', None)

    if not SECRET_KEY:
        SECRET_KEY = os.urandom(24)
        print('WARNING: SECRET_KEY being set as a one-shot', file=sys.stderr)

    print('SQLAlchemy URL (prod/base): {}'.format(_Config.SQLALCHEMY_DATABASE_URI))
    TESTING = False
    DEBUG = False
