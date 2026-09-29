from sqlalchemy.orm import Session
from typing import Optional
from app.models import Cliente, Movimentacao
from app.exceptions import RegraDeNegocioError

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
    total = db.query(Movimentacao).filter(Movimentacao.cliente_id == cliente.id).count()
    if total:
        raise RegraDeNegocioError(
            f"Não é possível remover: o cliente possui {total} movimentação(ões) registrada(s).",
            status_code=409,
        )
    db.delete(cliente)
    db.commit()
