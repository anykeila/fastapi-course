"""add content culumn to post table

Revision ID: 3bdcf7358311
Revises: 8e33102bc1e8
Create Date: 2023-09-06 17:56:20.369952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bdcf7358311'
down_revision: Union[str, None] = '8e33102bc1e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column("posts", "content")
    pass
