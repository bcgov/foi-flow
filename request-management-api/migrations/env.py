from __future__ import with_statement

import logging
from logging.config import fileConfig

from flask import current_app
from sqlalchemy import text

from alembic import context
from alembic.util import CommandError

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Shared by every online runner for this service, regardless of database role.
MIGRATION_LOCK_KEY = 0x464F494D494752

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option(
    'sqlalchemy.url',
    str(current_app.extensions['migrate'].db.engine.url).replace('%', '%%'))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = current_app.extensions['migrate'].db.engine

    with connectable.connect() as connection:
        completed = False
        try:
            locked = connection.execute(
                text('SELECT pg_try_advisory_lock(:key)'),
                {'key': MIGRATION_LOCK_KEY},
            ).scalar_one()
            # End SQLAlchemy's implicit transaction before Alembic starts its own.
            # The session advisory lock survives commits between revisions.
            connection.commit()
            if not locked:
                raise CommandError(
                    'Another database migration is running; retry after it completes.'
                )

            logger.info('Database migration lock acquired; starting online migration run.')
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                process_revision_directives=process_revision_directives,
                **current_app.extensions['migrate'].configure_args
            )

            with context.begin_transaction():
                context.run_migrations()
            completed = True
        finally:
            if not completed:
                # Close the physical session to release its lock even after a
                # failed transaction or disconnect, without masking the failure.
                connection.invalidate()
            else:
                try:
                    unlocked = connection.execute(
                        text('SELECT pg_advisory_unlock(:key)'),
                        {'key': MIGRATION_LOCK_KEY},
                    ).scalar_one()
                    connection.commit()
                    if not unlocked:
                        raise CommandError('Database migration lock was lost during execution.')
                except BaseException:
                    connection.invalidate()
                    raise
                logger.info('Online migration run completed; database migration lock released.')


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
