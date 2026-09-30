from decimal import Decimal
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Produto(Base):
    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="ck_produtos_quantidade_nao_negativa"),
        CheckConstraint("estoque_minimo >= 0", name="ck_produtos_estoque_minimo_nao_negativo"),
        CheckConstraint("preco_custo >= 0", name="ck_produtos_preco_custo_nao_negativo"),
        CheckConstraint("preco_venda >= 0", name="ck_produtos_preco_venda_nao_negativo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    quantidade = Column(Numeric(12, 3), default=Decimal("0"))  # só muda via Movimentação
    unidade = Column(String, default="unidade")
    estoque_minimo = Column(Numeric(12, 3), default=Decimal("0"))
    preco_custo = Column(Numeric(12, 2), default=Decimal("0"))
    preco_venda = Column(Numeric(12, 2), default=Decimal("0"))
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fornecedor = relationship("Fornecedor", back_populates="produtos")

    @property
    def abaixo_do_minimo(self) -> bool: 
        return (self.estoque_minimo or 0) > 0 and (self.quantidade or 0) < self.estoque_minimo

class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    contato = Column(String, nullable=True)

    produtos = relationship("Produto", back_populates="fornecedor")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    contato = Column(String, nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    papel = Column(String, default="operador")  # "operador" ou "gestor"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_movimentacoes_quantidade_positiva"),
        CheckConstraint("valor_unitario >= 0", name="ck_movimentacoes_valor_unitario_nao_negativo"),
        CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_movimentacoes_tipo_valido"),
    )

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    tipo = Column(String, nullable=False)  # "entrada" ou "saida"
    quantidade = Column(Numeric(12, 3), nullable=False)
    valor_unitario = Column(Numeric(12, 2), default=Decimal("0"))
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    produto = relationship("Produto")
    usuario = relationship("Usuario")
    cliente = relationship("Cliente")
