from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import SessionLocal
from app.models.models import Cliente
from app.schemas.schemas import ClienteCreate, ClienteResponse
from app.services import cliente as cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ClienteResponse)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    return cliente_service.criar_cliente(db, cliente.model_dump())

@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(nome: Optional[str] = None, db: Session = Depends(get_db)):
    return cliente_service.listar_clientes(db, nome)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(cliente_id: int, dados: ClienteCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente_service.atualizar_cliente(db, cliente, dados.model_dump())

@router.delete("/{cliente_id}")
def remover_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    cliente_service.remover_cliente(db, cliente)
    return {"mensagem": "Cliente removido com sucesso"}