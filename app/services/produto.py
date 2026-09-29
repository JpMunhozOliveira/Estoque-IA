from sqlalchemy.orm import Session
from typing import Optional
from app.models import Movimentacao, Produto
from app.schemas import MovimentacaoCreate
from app.exceptions import RegraDeNegocioError, validar

def criar_movimentacao(db: Session, dados: dict) -> Movimentacao:
    # O schema já garante: tipo "entrada"/"saida", quantidade > 0, valor >= 0
    mov = validar(MovimentacaoCreate, dados)

    produto = db.query(Produto).filter(Produto.id == mov.produto_id).first()
    if not produto:
        raise RegraDeNegocioError("Produto não encontrado", status_code=404)

    if mov.tipo == "saida" and produto.quantidade < mov.quantidade:
        raise RegraDeNegocioError("Quantidade insuficiente em estoque", status_code=400)

    if mov.tipo == "entrada":
        produto.quantidade += mov.quantidade
    else:
        produto.quantidade -= mov.quantidade

    nova = Movimentacao(**mov.model_dump())
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
