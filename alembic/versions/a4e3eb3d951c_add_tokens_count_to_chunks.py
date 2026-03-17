"""add_tokens_count_to_chunks

Revision ID: a4e3eb3d951c
Revises: 1062951c28c7
Create Date: 2026-03-14 15:35:48.848571

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4e3eb3d951c"
down_revision: Union[str, Sequence[str], None] = "1062951c28c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("chunk_index", sa.Column("tokens_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("chunk_index", "tokens_count")
