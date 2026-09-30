from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import ProdutoCreate, ProdutoResponse
from app.services import produto as produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos"])

@router.post("/", response_model=ProdutoResponse)
def criar_produto(
    produto: ProdutoCreate, 
    db: Session = Depends(get_db)
):
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
    return produto_service.listar_produtos(db, nome, categoria, fornecedor_id, preco_min, preco_max, abaixo_minimo,)

@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(
    produto_id: int, 
    dados: ProdutoCreate, 
    db: Session = Depends(get_db)
):
    produto = produto_service.buscar_produto(db, produto_id)
    return produto_service.atualizar_produto(db, produto, dados.model_dump())

@router.delete("/{produto_id}")
def remover_produto(
    produto_id: int, 
    db: Session = Depends(get_db)
):
    produto = produto_service.buscar_produto(db, produto_id)
    produto_service.remover_produto(db, produto)
    return {"mensagem": "Produto removido com sucesso"}