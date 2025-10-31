"""add_strategy_management_fields

Revision ID: 377064d9fc78
Revises: 0613ad962143
Create Date: 2025-10-30 22:58:07.320637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '377064d9fc78'
down_revision: Union[str, Sequence[str], None] = '0613ad962143'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to strategies table
    op.add_column('strategies', sa.Column('strategy_type', sa.String(length=100), nullable=False, server_default='buy_hold'))
    op.add_column('strategies', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('strategies', sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('strategies', sa.Column('is_template', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('strategies', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

    # Add indexes for better query performance
    op.create_index(op.f('ix_strategies_strategy_type'), 'strategies', ['strategy_type'], unique=False)
    op.create_index(op.f('ix_strategies_is_favorite'), 'strategies', ['is_favorite'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_strategies_is_favorite'), table_name='strategies')
    op.drop_index(op.f('ix_strategies_strategy_type'), table_name='strategies')

    # Drop columns
    op.drop_column('strategies', 'version')
    op.drop_column('strategies', 'is_template')
    op.drop_column('strategies', 'is_favorite')
    op.drop_column('strategies', 'tags')
    op.drop_column('strategies', 'strategy_type')
