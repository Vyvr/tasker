"""Rename status to status_id in tasks

Revision ID: d0d1db1156eb
Revises: 507c690ab493
Create Date: 2026-03-25 13:22:46.596261

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d0d1db1156eb"
down_revision: Union[str, Sequence[str], None] = "507c690ab493"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("tasks", "status", new_column_name="status_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("tasks", "status_id", new_column_name="status")
