from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Produto, Fornecedor, Movimentacao
from app.schemas.schemas import ProdutoCreate
from app.core.exceptions import RegraDeNegocioError, validar

def _checar_fornecedor(db: Session, fornecedor_id):
    if fornecedor_id and not db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first():
        raise RegraDeNegocioError("Fornecedor não encontrado", status_code=404)

def criar_produto(db: Session, dados: dict) -> Produto:
    p = validar(ProdutoCreate, dados)
    _checar_fornecedor(db, p.fornecedor_id)
    novo = Produto(**p.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_produtos(db: Session, nome: Optional[str] = None, categoria: Optional[str] = None,
                    fornecedor_id: Optional[int] = None, preco_min=None, preco_max=None,
                    abaixo_minimo: bool = False):
    query = db.query(Produto)
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    if categoria:
        query = query.filter(Produto.categoria.ilike(f"%{categoria}%"))
    if fornecedor_id:
        query = query.filter(Produto.fornecedor_id == fornecedor_id)
    if preco_min is not None:
        query = query.filter(Produto.preco_venda >= preco_min)
    if preco_max is not None:
        query = query.filter(Produto.preco_venda <= preco_max)
    if abaixo_minimo:
        query = query.filter(Produto.estoque_minimo > 0,
                             Produto.quantidade < Produto.estoque_minimo)
    return query.order_by(Produto.nome).all()

def atualizar_produto(db: Session, produto: Produto, dados: dict) -> Produto:
    p = validar(ProdutoCreate, dados)
    _checar_fornecedor(db, p.fornecedor_id)
    for campo, valor in p.model_dump().items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto

def remover_produto(db: Session, produto: Produto):
    total = db.query(Movimentacao).filter(Movimentacao.produto_id == produto.id).count()
    if total:
        raise RegraDeNegocioError(
            f"Não é possível remover: o produto possui {total} movimentação(ões) registrada(s).",
            status_code=409,
        )
    db.delete(produto)
    db.commit()

def buscar_produto(db: Session, produto_id: int) -> Produto:
    produto = db.get(Produto, produto_id)
    if not produto:
        raise RegraDeNegocioError("Produto não encontrado", status_code=404)
    return produto