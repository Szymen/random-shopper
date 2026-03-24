"""add users table and refactor purchases

Revision ID: fae1b369041d
Revises: 
Create Date: 2026-03-19 16:59:06.049359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fae1b369041d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Initial migration: create tables from scratch.

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('userid', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('customer', 'root', name='role'), nullable=False),
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_userid'), 'users', ['userid'], unique=True)

    op.create_table(
        'purchases',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )
    op.create_index(op.f('ix_purchases_user_id'), 'purchases', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_purchases_user_id'), table_name='purchases')
    op.drop_table('purchases')

    op.drop_index(op.f('ix_users_userid'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')

    # Drop the enum type explicitly on Postgres.
    op.execute('DROP TYPE IF EXISTS role')
