"""add doc_category to documents

Revision ID: b4f3a2c18de7
Revises: a6b1d2717843
Create Date: 2026-09-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b4f3a2c18de7'
down_revision: Union[str, Sequence[str], None] = 'a6b1d2717843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'documents',
        sa.Column('doc_category', sa.String(), nullable=False, server_default='policy')
    )


def downgrade() -> None:
    op.drop_column('documents', 'doc_category')
