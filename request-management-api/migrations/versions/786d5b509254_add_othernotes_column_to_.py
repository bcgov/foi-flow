"""Add ApplicantProfile columns to FOIRequestApplicants

Revision ID: 786d5b509254
Revises: 49274e42cd98
Create Date: 2026-01-23 10:40:56.152119

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '786d5b509254'
down_revision = '49274e42cd98'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('FOIRequestApplicants', sa.Column('email', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('category', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('address_secondary', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('city', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('province', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('postal', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('country', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('home_phone', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('mobile_phone', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('work_phone', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('alternative_phone', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('other_contact_info', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('personal_health_number', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('employee_number', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('correction_number', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('other_notes', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('section43_info', sa.Text(), nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('request_history', JSONB, nullable=True))
    op.add_column('FOIRequestApplicants', sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.true()))

def downgrade():
    op.drop_column('FOIRequestApplicants', 'email')
    op.drop_column('FOIRequestApplicants', 'category')
    op.drop_column('FOIRequestApplicants', 'address')
    op.drop_column('FOIRequestApplicants', 'address_secondary')
    op.drop_column('FOIRequestApplicants', 'city')
    op.drop_column('FOIRequestApplicants', 'province')
    op.drop_column('FOIRequestApplicants', 'postal')
    op.drop_column('FOIRequestApplicants', 'country')
    op.drop_column('FOIRequestApplicants', 'home_phone')
    op.drop_column('FOIRequestApplicants', 'mobile_phone')
    op.drop_column('FOIRequestApplicants', 'work_phone')
    op.drop_column('FOIRequestApplicants', 'alternative_phone')
    op.drop_column('FOIRequestApplicants', 'other_contact_info')
    op.drop_column('FOIRequestApplicants', 'personal_health_number')
    op.drop_column('FOIRequestApplicants', 'employee_number')
    op.drop_column('FOIRequestApplicants', 'correction_number')
    op.drop_column('FOIRequestApplicants', 'other_notes')
    op.drop_column('FOIRequestApplicants', 'section43_info')
    op.drop_column('FOIRequestApplicants', 'request_history')
    op.drop_column('FOIRequestApplicants', 'is_active')