from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Fornecedor
from app.schemas import FornecedorCreate, FornecedorResponse
from app.services import fornecedor as fornecedor_service

router = APIRouter(prefix="/fornecedor", tags=["Fornecedor"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FornecedorResponse)
def criar_fornecedor(fornecedor: FornecedorCreate, db: Session = Depends(get_db)):
    return fornecedor_service.criar_fornecedor(db, fornecedor.model_dump())

@router.get("/", response_model=list[FornecedorResponse])
def listar_fornecedores(nome: Optional[str] = None, db: Session = Depends(get_db)):
    return fornecedor_service.listar_fornecedores(db, nome)

@router.get("/{fornecedor_id}", response_model=FornecedorResponse)
def buscar_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor

@router.put("/{fornecedor_id}", response_model=FornecedorResponse)
def atualizar_fornecedor(fornecedor_id: int, dados: FornecedorCreate, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor_service.atualizar_fornecedor(db, fornecedor, dados.model_dump())

@router.delete("/{fornecedor_id}")
def remover_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    fornecedor_service.remover_fornecedor(db, fornecedor)
    return {"mensagem": "Fornecedor removido com sucesso"}