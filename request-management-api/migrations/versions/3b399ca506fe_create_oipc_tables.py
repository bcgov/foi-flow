"""Create OIPC tables

Revision ID: 3b399ca506fe
Revises: 29b44e8dc305
Create Date: 2023-11-14 22:29:58.451320

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, Column, Integer, String, MetaData
meta = MetaData()
from sqlalchemy.sql.schema import ForeignKey


# revision identifiers, used by Alembic.
revision = '3b399ca506fe'
down_revision = '29b44e8dc305'
branch_labels = None
depends_on = None


def upgrade():
    reviewtypestable = op.create_table('OIPCReviewTypes',
    sa.Column('reviewtypeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('reviewtypeid')
    )

    reasonstable = op.create_table('OIPCReasons',
    sa.Column('reasonid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('reasonid')
    )

    reviewtypes_reasons_table = op.create_table('OIPCReviewTypesReasons',
    sa.Column('reviewtypereasonid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reviewtypeid', sa.Integer(), ForeignKey('OIPCReviewTypes.reviewtypeid'), unique=False, nullable=False),
    sa.Column('reasonid', sa.Integer(), ForeignKey('OIPCReasons.reasonid'), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('reviewtypereasonid'),
    )

    statusestable = op.create_table('OIPCStatuses',
    sa.Column('statusid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('statusid')
    )

    outcomestable = op.create_table('OIPCOutcomes',
    sa.Column('outcomeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('outcomeid')
    )

    inquiryoutcomestable = op.create_table('OIPCInquiryOutcomes',
    sa.Column('inquiryoutcomeid', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), unique=False, nullable=False),
    sa.Column('isactive', sa.Boolean(), unique=False, nullable=False),
    sa.PrimaryKeyConstraint('inquiryoutcomeid')
    )

    op.execute('''INSERT INTO public."OIPCReviewTypes" (name, isactive)
               VALUES
                ('Complaint', True),
                ('Review', True),
                ('Investigation', True);commit;''')

    op.execute('''INSERT INTO public."OIPCReasons" (name, isactive)
               VALUES
                ('Adequate Search', True),
                ('Application of Exceptions', True),
                ('Deemed Refusal', True),
                ('Extension', True),
                ('Fee Amount', True),
                ('Fee Waiver', True),
                ('Records do not Exist', True),
                ('Duty to Assist', True),
                ('TPN - 22', True),
                ('TPN - 21', True),
                ('TPN - 18.1', True),
                ('Reg 3', True),
                ('Reg 4', True),
                ('Reg 5', True),
                ('s. 43', True),
                ('Other', True);commit;''')

    op.execute('''INSERT INTO public."OIPCStatuses" (name, isactive)
               VALUES
                ('Mediation', True),
                ('Investigation', True),
                ('Inquiry', True),
                ('Awaiting Order', True),
                ('Closed', True);commit;''')

    op.execute('''INSERT INTO public."OIPCOutcomes" (name, isactive)
               VALUES
                ('Abandoned', True),
                ('Withdrawn', True),
                ('Resolved in Mediation', True),
                ('Closed', True),
                ('Amend', True);commit;''')

    op.execute('''INSERT INTO public."OIPCInquiryOutcomes" (name, isactive)
               VALUES
                ('Decision Upheld', True),
                ('Decision Partially Upheld', True),
                ('Decision Overturned', True);commit;''')

    op.execute('''INSERT INTO public."OIPCReviewTypesReasons" (reviewtypeid, reasonid, isactive)
                VALUES
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Adequate Search'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Extension'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Fee Amount'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Fee Waiver'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Duty to Assist'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Complaint'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Other'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Application of Exceptions'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Deemed Refusal'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'TPN - 22'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'TPN - 21'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'TPN - 18.1'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Reg 3'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Reg 4'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Reg 5'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 's. 43'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Review'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Other'),
                        True
                    ),
                    (
                        (SELECT reviewtypeid FROM public."OIPCReviewTypes" WHERE name = 'Investigation'),
                        (SELECT reasonid FROM public."OIPCReasons" WHERE name = 'Other'),
                        True
                    );commit;''')

def downgrade():
    op.drop_table('OIPCReviewTypesReasons')
    op.drop_table('OIPCReviewTypes')
    op.drop_table('OIPCReasons')
    op.drop_table('OIPCStatuses')
    op.drop_table('OIPCOutcomes')
    op.drop_table('OIPCInquiryOutcomes')
