"""remover fornecedor do produto

Revision ID: a7d3b9c10e22
Revises: f272a009d406
Create Date: 2026-10-05 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a7d3b9c10e22'
down_revision: Union[str, Sequence[str], None] = 'f272a009d406'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No Postgres, dropar a coluna também derruba a FK
    op.drop_column('produtos', 'fornecedor_id')


def downgrade() -> None:
    op.add_column('produtos', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key('produtos_fornecedor_id_fkey', 'produtos',
                          'fornecedores', ['fornecedor_id'], ['id'])