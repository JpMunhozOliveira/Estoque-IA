from sqlalchemy.orm import Session
from app.models import Produto

def criar_produto(db: Session, dados: dict) -> Produto:
    novo = Produto(**dados)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_produtos(db: Session, nome=None, categoria=None, fornecedor_id=None, preco_min=None, preco_max=None):
    query = db.query(Produto)
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    if fornecedor_id:
        query = query.filter(Produto.fornecedor_id == fornecedor_id)
    if preco_min is not None:
        query = query.filter(Produto.preco_venda >= preco_min)
    if preco_max is not None:
        query = query.filter(Produto.preco_venda <= preco_max)
    return query.all()

def atualizar_produto(db: Session, produto: Produto, dados: dict) -> Produto:
    for campo, valor in dados.items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto

def remover_produto(db: Session, produto: Produto):
    db.delete(produto)
    db.commit()