"""Add stock non negative check

Revision ID: 4877af4546c5
Revises: b9953ac12c5e
Create Date: 2026-10-17 09:42:48.796547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4877af4546c5'
down_revision = 'b9953ac12c5e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        'CK_SANPHAM_SOLUONGTON', 'SANPHAM', 'SOLUONGTON >= 0'
    )


def downgrade():
    op.drop_constraint('CK_SANPHAM_SOLUONGTON', 'SANPHAM', type_='check')
