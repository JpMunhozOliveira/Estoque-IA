from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Movimentacao, Produto
from app.schemas import MovimentacaoCreate, MovimentacaoResponse

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=MovimentacaoResponse)
def criar_movimentacao(mov: MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == mov.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if mov.tipo not in ("entrada", "saida"):
        raise HTTPException(status_code=400, detail="Tipo deve ser 'entrada' ou 'saida'")

    if mov.tipo == "saida" and produto.quantidade < mov.quantidade:
        raise HTTPException(status_code=400, detail="Quantidade insuficiente em estoque")

    if mov.tipo == "entrada":
        produto.quantidade += mov.quantidade
    else:
        produto.quantidade -= mov.quantidade

    nova = Movimentacao(**mov.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/", response_model=list[MovimentacaoResponse])
def listar_movimentacoes(produto_id: Optional[int] = None, tipo: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Movimentacao)
    if produto_id:
        query = query.filter(Movimentacao.produto_id == produto_id)
    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)
    return query.order_by(Movimentacao.data.desc()).all()