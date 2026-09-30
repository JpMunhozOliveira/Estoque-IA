from sqlalchemy.orm import Session
from typing import Optional
from app.models import Fornecedor, Produto
from app.exceptions import RegraDeNegocioError

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
    total = db.query(Produto).filter(Produto.fornecedor_id == fornecedor.id).count()
    if total:
        raise RegraDeNegocioError(
            f"Não é possível remover: o fornecedor possui {total} produto(s) vinculado(s).",
            status_code=409,
        )
    db.delete(fornecedor)
    db.commit()

def buscar_fornecedor(db: Session, fornecedor_id: int) -> Fornecedor:
    fornecedor = db.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise RegraDeNegocioError("Fornecedor não encontrado", status_code=404)
    return fornecedor