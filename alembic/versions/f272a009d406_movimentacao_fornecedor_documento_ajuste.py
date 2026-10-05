"""movimentacao fornecedor documento ajuste

Revision ID: f272a009d406
Revises: c5a8e2d0f731
Create Date: 2026-10-05 13:57:54.647621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f272a009d406'
down_revision: Union[str, Sequence[str], None] = 'c5a8e2d0f731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('movimentacoes', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.add_column('movimentacoes', sa.Column('documento', sa.String(60), nullable=True))
    op.add_column('movimentacoes', sa.Column('observacao', sa.String(500), nullable=True))
    op.add_column('movimentacoes', sa.Column('motivo_ajuste', sa.String(30), nullable=True))
    op.create_foreign_key('fk_movimentacoes_fornecedor_id', 'movimentacoes',
                          'fornecedores', ['fornecedor_id'], ['id'])

    # Troca as regras antigas pelas novas
    op.drop_constraint('ck_movimentacoes_quantidade_positiva', 'movimentacoes', type_='check')
    op.drop_constraint('ck_movimentacoes_tipo_valido', 'movimentacoes', type_='check')
    op.create_check_constraint(
        'ck_movimentacoes_quantidade_valida', 'movimentacoes',
        "(tipo = 'ajuste' AND quantidade <> 0) OR (tipo <> 'ajuste' AND quantidade > 0)")
    op.create_check_constraint(
        'ck_movimentacoes_tipo_valido', 'movimentacoes',
        "tipo IN ('entrada', 'saida', 'ajuste')")
    op.create_check_constraint(
        'ck_movimentacoes_motivo_so_no_ajuste', 'movimentacoes',
        "(tipo = 'ajuste') = (motivo_ajuste IS NOT NULL)")


def downgrade() -> None:
    """Downgrade schema."""
    # Atenção: se já existirem ajustes gravados, o downgrade falha ao recriar as regras antigas.
    op.drop_constraint('ck_movimentacoes_motivo_so_no_ajuste', 'movimentacoes', type_='check')
    op.drop_constraint('ck_movimentacoes_tipo_valido', 'movimentacoes', type_='check')
    op.drop_constraint('ck_movimentacoes_quantidade_valida', 'movimentacoes', type_='check')
    op.create_check_constraint('ck_movimentacoes_tipo_valido', 'movimentacoes',
                               "tipo IN ('entrada', 'saida')")
    op.create_check_constraint('ck_movimentacoes_quantidade_positiva', 'movimentacoes',
                               "quantidade > 0")
    op.drop_constraint('fk_movimentacoes_fornecedor_id', 'movimentacoes', type_='foreignkey')
    op.drop_column('movimentacoes', 'motivo_ajuste')
    op.drop_column('movimentacoes', 'observacao')
    op.drop_column('movimentacoes', 'documento')
    op.drop_column('movimentacoes', 'fornecedor_id')
