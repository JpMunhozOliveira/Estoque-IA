from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Movimentacao, Produto
from app.schemas.schemas import MovimentacaoCreate
from app.core.exceptions import RegraDeNegocioError, validar
from app.models.models import Movimentacao, Produto, Cliente

def criar_movimentacao(db: Session, dados: dict, usuario_id: int) -> Movimentacao:
    mov = validar(MovimentacaoCreate, dados)

    # with_for_update trava a linha: duas saídas simultâneas não passam da validação juntas
    produto = (
        db.query(Produto).filter(Produto.id == mov.produto_id).with_for_update().first()
    )
    if not produto:
        raise RegraDeNegocioError("Produto não encontrado", status_code=404)

    if mov.cliente_id and not db.get(Cliente, mov.cliente_id):
        raise RegraDeNegocioError("Cliente não encontrado", status_code=404)

    if mov.tipo == "saida" and produto.quantidade < mov.quantidade:
        raise RegraDeNegocioError("Quantidade insuficiente em estoque", status_code=400)

    if mov.tipo == "entrada":
        produto.quantidade += mov.quantidade
    else:
        produto.quantidade -= mov.quantidade

    nova = Movimentacao(**mov.model_dump(), usuario_id=usuario_id)
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
