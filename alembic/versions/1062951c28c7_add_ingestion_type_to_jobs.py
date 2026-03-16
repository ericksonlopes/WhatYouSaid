"""add_ingestion_type_to_jobs

Revision ID: 1062951c28c7
Revises: 790acc587e00
Create Date: 2026-03-14 15:22:28.848571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1062951c28c7'
down_revision: Union[str, Sequence[str], None] = '790acc587e00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ingestion_jobs', sa.Column('ingestion_type', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('ingestion_jobs', 'ingestion_type')
