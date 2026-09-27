"""Increase HINHANH length to 500

Revision ID: f14dcd86bf53
Revises: 
Create Date: 2026-09-24 11:17:38.618474

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f14dcd86bf53'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('SANPHAM', schema=None) as batch_op:
        batch_op.alter_column('HINHANH',
               existing_type=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.String(length=500),
               existing_nullable=True)


def downgrade():
    with op.batch_alter_table('SANPHAM', schema=None) as batch_op:
        batch_op.alter_column('HINHANH',
               existing_type=sa.String(length=500),
               type_=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=True)