"""Initial migration

Revision ID: 3b35d545b975
Revises: c1f67a62d6f2
Create Date: 2024-11-27 15:33:42.584525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b35d545b975'
down_revision: Union[str, None] = 'c1f67a62d6f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
