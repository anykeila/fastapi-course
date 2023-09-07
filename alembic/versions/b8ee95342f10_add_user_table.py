"""add user table

Revision ID: b8ee95342f10
Revises: 3bdcf7358311
Create Date: 2023-09-06 18:01:56.168887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8ee95342f10'
down_revision: Union[str, None] = '3bdcf7358311'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), nullable=False),
                             sa.Column("email", sa.String(), nullable=False),
                             sa.Column("password", sa.String(), nullable=False),
                             sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                                       server_default=sa.text("now()"), nullable=False),
                             sa.PrimaryKeyConstraint("id"),
                             sa.UniqueConstraint("email")
                    )
    pass


def downgrade():
    op.drop_table("users")
    pass
