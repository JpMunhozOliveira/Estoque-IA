from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException
from app.models import Movimentacao, Produto

def criar_movimentacao(db: Session, dados: dict) -> Movimentacao:
    produto = db.query(Produto).filter(Produto.id == dados["produto_id"]).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if dados["tipo"] not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'")

    if dados["tipo"] == "saida" and produto.quantidade < dados["quantidade"]:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque")

    if dados["tipo"] == "entrada":
        produto.quantidade += dados["quantidade"]
    else:
        produto.quantidade -= dados["quantidade"]

    nova = Movimentacao(**dados)
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

def listar_movimentacoes(db: Session, produto_id: Optional[int] = None, tipo: Optional[str] = None):
    query = db.query(Movimentacao)
    if produto_id:
        query = query.filter(Movimentacao.produto_id == produto_id)
    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)
    return query.order_by(Movimentacao.data.desc()).all()