"""Initial migration

Revision ID: c1f67a62d6f2
Revises: e7f604d63913
Create Date: 2024-11-27 15:28:58.600868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1f67a62d6f2'
down_revision: Union[str, None] = 'e7f604d63913'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
