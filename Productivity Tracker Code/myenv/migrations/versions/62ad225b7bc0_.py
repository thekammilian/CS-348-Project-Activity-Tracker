"""empty message

Revision ID: 62ad225b7bc0
Revises: 835bcede8c74
Create Date: 2023-12-07 16:48:58.362455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62ad225b7bc0'
down_revision = '835bcede8c74'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('activity_name', sa.String(length=255), nullable=False))
        batch_op.create_index('idx_activity_date', ['activity_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('activity', schema=None) as batch_op:
        batch_op.drop_index('idx_activity_date')
        batch_op.drop_column('activity_name')

    # ### end Alembic commands ###
