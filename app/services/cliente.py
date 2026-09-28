from sqlalchemy.orm import Session
from typing import Optional
from app.models import Cliente

def criar_cliente(db: Session, dados: dict) -> Cliente:
    novo = Cliente(**dados)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_clientes(db: Session, nome: Optional[str] = None):
    query = db.query(Cliente)
    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    return query.all()

def atualizar_cliente(db: Session, cliente: Cliente, dados: dict) -> Cliente:
    for campo, valor in dados.items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente

def remover_cliente(db: Session, cliente: Cliente):
    db.delete(cliente)
    db.commit()