"""Add delivery info (HOTENNHAN, DIACHIGIAO, SDTNHAN) to DONHANG

Revision ID: b2a434abe7a9
Revises: f14dcd86bf53
Create Date: 2026-09-29 21:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2a434abe7a9'
down_revision = 'f14dcd86bf53'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('DONHANG', schema=None) as batch_op:
        batch_op.add_column(sa.Column('HOTENNHAN', sa.Unicode(length=200), nullable=True))
        batch_op.add_column(sa.Column('DIACHIGIAO', sa.Unicode(length=300), nullable=True))
        batch_op.add_column(sa.Column('SDTNHAN', sa.String(length=15), nullable=True))


def downgrade():
    with op.batch_alter_table('DONHANG', schema=None) as batch_op:
        batch_op.drop_column('SDTNHAN')
        batch_op.drop_column('DIACHIGIAO')
        batch_op.drop_column('HOTENNHAN')