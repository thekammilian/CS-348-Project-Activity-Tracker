"""empty message

Revision ID: 737970be4a9e
Revises: 62ad225b7bc0
Create Date: 2023-12-07 16:52:15.300066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '737970be4a9e'
down_revision = '62ad225b7bc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_name', sa.String(length=255), nullable=False, default=''))
        batch_op.create_index('idx_activity_date', ['activity_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.drop_index('idx_activity_date')
        batch_op.drop_column('activity_name')

    # ### end Alembic commands ###