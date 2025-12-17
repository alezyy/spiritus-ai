"""add_verified_field_to_user

Revision ID: add_verified_column
Revises: 37f288994c47
Create Date: 2025-12-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'add_verified_column'
down_revision: Union[str, None] = '37f288994c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column exists to avoid errors if run multiple times
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'verified' not in columns:
        op.add_column('user', sa.Column('verified', sa.Boolean(), nullable=True, server_default=sa.text('0')))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('user')]
    
    if 'verified' in columns:
        op.drop_column('user', 'verified')
