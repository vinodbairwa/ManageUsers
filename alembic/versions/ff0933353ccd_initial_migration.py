"""Initial migration

Revision ID: ff0933353ccd
Revises: 3b35d545b975
Create Date: 2024-11-27 15:40:16.604426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff0933353ccd'
down_revision: Union[str, None] = '3b35d545b975'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
