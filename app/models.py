from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=True)
    quantidade = Column(Float, default=0)
    unidade = Column(String, default="unidade")
    estoque_minimo = Column(Float, default=0)
    preco_custo = Column(Float, default=0)
    preco_venda = Column(Float, default=0)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fornecedor = relationship("Fornecedor", back_populates="produtos")

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

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    tipo = Column(String, nullable=False)  # "entrada" ou "saida"
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, default=0)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    produto = relationship("Produto")
    usuario = relationship("Usuario")
    cliente = relationship("Cliente")