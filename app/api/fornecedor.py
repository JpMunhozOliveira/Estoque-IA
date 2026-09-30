from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import FornecedorCreate, FornecedorResponse
from app.services import fornecedor as fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.post("/", response_model=FornecedorResponse)
def criar_fornecedor(
    fornecedor: FornecedorCreate, 
    db: Session = Depends(get_db)
):
    return fornecedor_service.criar_fornecedor(db, fornecedor.model_dump())

@router.get("/", response_model=list[FornecedorResponse])
def listar_fornecedores(
    nome: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return fornecedor_service.listar_fornecedores(db, nome)

@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def buscar_fornecedor(
    fornecedor_id: int, 
    db: Session = Depends(get_db)
):
    return fornecedor_service.buscar_fornecedor(db, fornecedor_id)

@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(
    fornecedor_id: int, 
    dados: FornecedorCreate, 
    db: Session = Depends(get_db)
):
    fornecedor = fornecedor_service.buscar_fornecedor(db, fornecedor_id)
    return fornecedor_service.atualizar_fornecedor(db, fornecedor, dados.model_dump())

@router.delete("/{fornecedor_id}")
def remover_fornecedor(
    fornecedor_id: int, 
    db: Session = Depends(get_db)
):
    fornecedor = fornecedor_service.buscar_fornecedor(db, fornecedor_id)
    fornecedor_service.remover_fornecedor(db, fornecedor)
    return {"mensagem": "Fornecedor removido com sucesso"}