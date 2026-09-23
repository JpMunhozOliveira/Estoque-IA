from sqlalchemy import Column, Integer, String, Float, DateTime
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
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))