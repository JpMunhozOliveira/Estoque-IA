from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Fornecedor
from app.schemas import FornecedorCreate, FornecedorResponse
from app.services import fornecedor as fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FornecedorResponse)
def criar_fornecedor(fornecedor: FornecedorCreate, db: Session = Depends(get_db)):
    novo = Fornecedor(**fornecedor.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/", response_model=list[FornecedorResponse])
def listar_fornecedores(nome: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Fornecedor)
    if nome:
        query = query.filter(Fornecedor.nome.ilike(f"%{nome}%"))
    return query.all()

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
    for campo, valor in dados.model_dump().items():
        setattr(fornecedor, campo, valor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor

@router.delete("/{fornecedor_id}")
def remover_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    db.delete(fornecedor)
    db.commit()
    return {"mensagem": "Fornecedor removido com sucesso"}