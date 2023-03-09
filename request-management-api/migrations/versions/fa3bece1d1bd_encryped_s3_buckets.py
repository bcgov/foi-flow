"""encryped s3 buckets

Revision ID: fa3bece1d1bd
Revises: 79ad99148fa4
Create Date: 2023-03-08 12:02:27.499614

"""
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision = 'fa3bece1d1bd'
down_revision = '79ad99148fa4'
branch_labels = None
depends_on = None

s3environment = os.getenv('OSS_S3_ENVIRONMENT')

def upgrade():

    #DocumentPathMapper
    op.execute('''
        DO $BODY$
        DECLARE
            r public."ProgramAreas"%rowtype;
            env text := \'''' + s3environment + '''\';
        BEGIN
            FOR r IN (select * from public."ProgramAreas" where isactive = true)
            LOOP
                update public."DocumentPathMapper" set bucket = REPLACE(bucket, lower(r.bcgovcode || '-' || env), lower(r.bcgovcode || '-' || env || '-e'))
                where bucket = lower(r.bcgovcode || '-' || env);
            END LOOP;
        END; $BODY$
    ''')

    #DocumentPathMapper
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = env || '-forms-foirequests-e'
            where bucket = env || '-forms-foirequests';
        END; $BODY$
    ''')

    #FOIRequestRecords
    op.execute('''
        DO $BODY$
        DECLARE
            r public."ProgramAreas"%rowtype;
            env text := \'''' + s3environment + '''\';
        BEGIN
            FOR r IN (select * from public."ProgramAreas" where isactive = true)
            LOOP
                update public."FOIRequestRecords" set s3uripath = REPLACE(s3uripath, lower(r.bcgovcode || '-' || env || '/'), lower(r.bcgovcode || '-' || env || '-e/'))
                where s3uripath like '%' || lower(r.bcgovcode || '-' || env || '/%');
            END LOOP;
        END; $BODY$
    ''')

    #FOIMinistryRequestDocuments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIMinistryRequestDocuments" set documentpath = REPLACE(documentpath, env || '-forms-foirequests/', env || '-forms-foirequests-e/')
            where documentpath like '%' || env || '-forms-foirequests/%';
        END; $BODY$
    ''')

    #FOIRawRequestDocuments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIRawRequestDocuments" set documentpath = REPLACE(documentpath, env || '-forms-foirequests/', env || '-forms-foirequests-e/')
            where documentpath like '%' || env || '-forms-foirequests/%';
        END; $BODY$
    ''')

    #FOIApplicantCorrespondenceAttachments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIApplicantCorrespondenceAttachments" set attachmentdocumenturipath = REPLACE(attachmentdocumenturipath, env || '-forms-foirequests/', env || '-forms-foirequests-e/')
            where attachmentdocumenturipath like '%' || env || '-forms-foirequests/%';
        END; $BODY$
    ''')

def downgrade():

    #DocumentPathMapper
    op.execute('''
        DO $BODY$
        DECLARE
            r public."ProgramAreas"%rowtype;
            env text := \'''' + s3environment + '''\';
        BEGIN
            FOR r IN (select * from public."ProgramAreas" where isactive = true)
            LOOP
                update public."DocumentPathMapper" set bucket = REPLACE(bucket, lower(r.bcgovcode || '-' || env || '-e'), lower(r.bcgovcode || '-' || env))
                where bucket = lower(r.bcgovcode || '-' || env || '-e');
            END LOOP;
        END; $BODY$
    ''')

    #DocumentPathMapper
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."DocumentPathMapper" set bucket = env || '-forms-foirequests'
            where bucket = env || '-forms-foirequests-e';
        END; $BODY$
    ''')

    #FOIRequestRecords
    op.execute('''
        DO $BODY$
        DECLARE
            r public."ProgramAreas"%rowtype;
            env text := \'''' + s3environment + '''\';
        BEGIN
            FOR r IN (select * from public."ProgramAreas" where isactive = true)
            LOOP
                update public."FOIRequestRecords" set s3uripath = REPLACE(s3uripath, lower(r.bcgovcode || '-' || env || '-e/'), lower(r.bcgovcode || '-' || env || '/'))
                where s3uripath like '%' || lower(r.bcgovcode || '-' || env || '-e/%');
            END LOOP;
        END; $BODY$
    ''')

    #FOIMinistryRequestDocuments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIMinistryRequestDocuments" set documentpath = REPLACE(documentpath, env || '-forms-foirequests-e/', env || '-forms-foirequests/')
            where documentpath like '%' || env || '-forms-foirequests-e/%';
        END; $BODY$
    ''')

    #FOIRawRequestDocuments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIRawRequestDocuments" set documentpath = REPLACE(documentpath, env || '-forms-foirequests-e/', env || '-forms-foirequests/')
            where documentpath like '%' || env || '-forms-foirequests-e/%';
        END; $BODY$
    ''')

    #FOIApplicantCorrespondenceAttachments
    op.execute('''
        DO $BODY$
        DECLARE
            env text := \'''' + s3environment + '''\';
        BEGIN
            update public."FOIApplicantCorrespondenceAttachments" set attachmentdocumenturipath = REPLACE(attachmentdocumenturipath, env || '-forms-foirequests-e/', env || '-forms-foirequests/')
            where attachmentdocumenturipath like '%' || env || '-forms-foirequests-e/%';
        END; $BODY$
    ''')