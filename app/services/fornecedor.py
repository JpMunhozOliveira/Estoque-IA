from sqlalchemy.orm import Session
from typing import Optional
from app.models import Fornecedor

def criar_fornecedor(db: Session, dados: dict) -> Fornecedor:
    novo = Fornecedor(**dados)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_fornecedores(db: Session, nome: Optional[str] = None):
    query = db.query(Fornecedor)
    if nome:
        query = query.filter(Fornecedor.nome.ilike(f"%{nome}%"))
    return query.all()

def atualizar_fornecedor(db: Session, fornecedor: Fornecedor, dados: dict) -> Fornecedor:
    for campo, valor in dados.items():
        setattr(fornecedor, campo, valor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

def remover_fornecedor(db: Session, fornecedor: Fornecedor):
    db.delete(fornecedor)
    db.commit()