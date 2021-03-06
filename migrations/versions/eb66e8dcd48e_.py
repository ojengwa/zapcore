"""empty message

Revision ID: eb66e8dcd48e
Revises: ac69db71cc53
Create Date: 2018-02-09 12:13:05.811720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb66e8dcd48e'
down_revision = 'ac69db71cc53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bill', sa.Column('policy_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'bill', 'policy', ['policy_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'bill', type_='foreignkey')
    op.drop_column('bill', 'policy_id')
    # ### end Alembic commands ###
