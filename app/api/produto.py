from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import SessionLocal
from app.models.models import Produto
from app.schemas.schemas import ProdutoCreate, ProdutoResponse
from app.services import produto as produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    return produto_service.criar_produto(db, produto.model_dump())


@router.get("/", response_model=list[ProdutoResponse])
def listar_produtos(
    nome: Optional[str] = None,
    categoria: Optional[str] = None,
    fornecedor_id: Optional[int] = None,
    preco_min: Optional[float] = None,
    preco_max: Optional[float] = None,
    abaixo_minimo: bool = False,
    db: Session = Depends(get_db)
):
    return produto_service.listar_produtos(db, nome, categoria, fornecedor_id,
                                       preco_min, preco_max, abaixo_minimo)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, dados: ProdutoCreate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto_service.atualizar_produto(db, produto, dados.model_dump())

@router.delete("/{produto_id}")
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto_service.remover_produto(db, produto)
    return {"mensagem": "Produto removido com sucesso"}