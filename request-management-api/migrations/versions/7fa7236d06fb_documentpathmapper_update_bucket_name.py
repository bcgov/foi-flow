"""DocumentPathMapper - update bucket name

Revision ID: 7fa7236d06fb
Revises: a79cd809e85e
Create Date: 2023-10-29 23:25:40.642169

"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = '7fa7236d06fb'
down_revision = 'a79cd809e85e'
branch_labels = None
depends_on = None


s3environment = os.getenv('OSS_S3_ENVIRONMENT')

def upgrade():

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'gcp-' || env || '-e'
            where bucket = 'gcpe-' || env || '-e';
        END; $BODY$
    ''')

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'msd-' || env || '-e'
            where bucket = 'sdpr-' || env || '-e';
        END; $BODY$
    ''')

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'oop-' || env || '-e'
            where bucket = 'prem-' || env || '-e';
        END; $BODY$
    ''')


def downgrade():

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'gcpe-' || env || '-e'
            where bucket = 'gcp-' || env || '-e';
        END; $BODY$
    ''')

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'sdpr-' || env || '-e'
            where bucket = 'msd-' || env || '-e';
        END; $BODY$
    ''')

    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = 'prem-' || env || '-e'
            where bucket = 'oop-' || env || '-e';
        END; $BODY$
    ''')
