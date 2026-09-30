from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Cliente, Movimentacao
from app.schemas.schemas import ClienteCreate
from app.core.exceptions import RegraDeNegocioError, validar

def criar_cliente(db: Session, dados: dict) -> Cliente:
    c = validar(ClienteCreate, dados)
    novo = Cliente(**c.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def atualizar_cliente(db: Session, cliente: Cliente, dados: dict) -> Cliente:
    c = validar(ClienteCreate, dados)
    for campo, valor in c.model_dump().items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente

def listar_clientes(db: Session, nome: Optional[str] = None):
    query = db.query(Cliente)
    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    return query.all()

def remover_cliente(db: Session, cliente: Cliente):
    total = db.query(Movimentacao).filter(Movimentacao.cliente_id == cliente.id).count()
    if total:
        raise RegraDeNegocioError(
            f"Não é possível remover: o cliente possui {total} movimentação(ões) registrada(s).",
            status_code=409,
        )
    db.delete(cliente)
    db.commit()

def buscar_cliente(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise RegraDeNegocioError("Cliente não encontrado", status_code=404)
    return cliente