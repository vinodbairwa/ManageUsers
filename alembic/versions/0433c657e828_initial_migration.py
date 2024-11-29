"""Initial migration

Revision ID: 0433c657e828
Revises: ff0933353ccd
Create Date: 2024-11-27 15:41:50.306062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0433c657e828'
down_revision: Union[str, None] = 'ff0933353ccd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
