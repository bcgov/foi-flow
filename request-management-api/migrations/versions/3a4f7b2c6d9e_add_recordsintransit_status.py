"""
Add Records in Transit Status

Revision ID: 3a4f7b2c6d9e
Revises: e34689b89160
Create Date: 2025-08-27 8:50:55.126582

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '3a4f7b2c6d9e'
down_revision = 'e34689b89160'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('INSERT INTO public."FOIRequestStatuses"(name, description, isactive, statuslabel) VALUES (\'Records in Transit\', \'Records in Transit\', True, \'recordsintransit\');commit;')
    # NOTE:
    # The below script will be executed manually in each environment, it is just here for reference
    # Fill in the ARRAY[] with duplicate values from FOIRequestApplicants, which you can find by running:

    # SELECT applicantprofileid, COUNT(*)
    # FROM public."FOIRequestApplicants"
    # GROUP BY applicantprofileid
    # HAVING COUNT(*) > 1
    # ORDER BY count DESC;

    # The script:
    # WITH guid_map AS (
    #     SELECT
    #         firstname,
    #         lastname,
    #         COALESCE(
    #             MAX(
    #                 CASE 
    #                     WHEN applicantprofileid = ANY(ARRAY[]) THEN NULL
    #                     ELSE applicantprofileid
    #                 END
    #             ),
    #             gen_random_uuid()::text
    #         ) AS new_id
    #     FROM public."FOIRequestApplicants"
    #     GROUP BY firstname, lastname
    # )
    # -- SELECT * FROM guid_map
    # UPDATE public."FOIRequestApplicants" t
    # SET applicantprofileid = g.new_id
    # FROM guid_map g
    # WHERE t.firstname = g.firstname
    # AND t.lastname = g.lastname
    # AND t.applicantprofileid = ANY(ARRAY[])
    # RETURNING *;


def downgrade():
    op.execute('DELETE FROM public."FOIRequestStatuses" WHERE name = \'Records in Transit\';commit;')