"""Seed DB with Countries, Users and Visits”


Revision ID: 8b473616f566
Revises: 67d7c19a54d7
Create Date: 2025-03-04 06:49:17.663167+00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from getdigitalnomadapi import seed


# revision identifiers, used by Alembic.
revision: str = "8b473616f566"
down_revision: Union[str, None] = "67d7c19a54d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    seed.create_countries()
    seed.create_users()
    seed.create_visits()


def downgrade() -> None:
    seed.delete_countries()
    seed.delete_users()
    seed.delete_visits()
