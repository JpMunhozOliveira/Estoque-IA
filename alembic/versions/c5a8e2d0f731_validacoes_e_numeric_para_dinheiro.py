"""validacoes (CHECK) e Numeric para dinheiro e quantidades

Revision ID: c5a8e2d0f731
Revises: e4a111417843
Create Date: 2026-09-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c5a8e2d0f731'
down_revision: Union[str, Sequence[str], None] = 'e4a111417843'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (tabela, coluna, tipo novo)
COLUNAS_NUMERIC = [
    ("produtos", "quantidade", sa.Numeric(12, 3)),
    ("produtos", "estoque_minimo", sa.Numeric(12, 3)),
    ("produtos", "preco_custo", sa.Numeric(12, 2)),
    ("produtos", "preco_venda", sa.Numeric(12, 2)),
    ("movimentacoes", "quantidade", sa.Numeric(12, 3)),
    ("movimentacoes", "valor_unitario", sa.Numeric(12, 2)),
]

# (nome, tabela, condição)
CHECKS = [
    ("ck_produtos_quantidade_nao_negativa", "produtos", "quantidade >= 0"),
    ("ck_produtos_estoque_minimo_nao_negativo", "produtos", "estoque_minimo >= 0"),
    ("ck_produtos_preco_custo_nao_negativo", "produtos", "preco_custo >= 0"),
    ("ck_produtos_preco_venda_nao_negativo", "produtos", "preco_venda >= 0"),
    ("ck_movimentacoes_quantidade_positiva", "movimentacoes", "quantidade > 0"),
    ("ck_movimentacoes_valor_unitario_nao_negativo", "movimentacoes", "valor_unitario >= 0"),
    ("ck_movimentacoes_tipo_valido", "movimentacoes", "tipo IN ('entrada', 'saida')"),
]


def upgrade() -> None:
    """Upgrade schema."""
    # 1) Float -> Numeric (o USING diz ao Postgres como converter os valores já gravados)
    for tabela, coluna, tipo in COLUNAS_NUMERIC:
        op.alter_column(
            tabela, coluna,
            existing_type=sa.Float(),
            type_=tipo,
            existing_nullable=True if not (tabela == "movimentacoes" and coluna == "quantidade") else False,
            postgresql_using=f"{coluna}::numeric({tipo.precision},{tipo.scale})",
        )

    # 2) Regras no próprio banco (última barreira, mesmo que algo passe pelo código)
    for nome, tabela, condicao in CHECKS:
        op.create_check_constraint(nome, tabela, condicao)


def downgrade() -> None:
    """Downgrade schema."""
    for nome, tabela, _ in CHECKS:
        op.drop_constraint(nome, tabela, type_="check")

    for tabela, coluna, tipo in COLUNAS_NUMERIC:
        op.alter_column(
            tabela, coluna,
            existing_type=tipo,
            type_=sa.Float(),
            existing_nullable=True if not (tabela == "movimentacoes" and coluna == "quantidade") else False,
            postgresql_using=f"{coluna}::double precision",
        )
