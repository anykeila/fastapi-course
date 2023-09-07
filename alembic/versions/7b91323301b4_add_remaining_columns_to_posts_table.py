"""add remaining columns to posts table

Revision ID: 7b91323301b4
Revises: 342215ec62a8
Create Date: 2023-09-06 18:24:27.480104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b91323301b4'
down_revision: Union[str, None] = '342215ec62a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("posts", sa.Column("published", sa.Boolean(), nullable=False, server_default='True'),)
    op.add_column("posts", sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                                    server_default=sa.text("now()"), nullable=False))
    pass


def downgrade():
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
    pass
