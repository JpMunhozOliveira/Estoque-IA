from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import ClienteCreate, ClienteResponse
from app.services import cliente as cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=ClienteResponse)
def criar_cliente(
    cliente: ClienteCreate, 
    db: Session = Depends(get_db)
    ):
    return cliente_service.criar_cliente(db, cliente.model_dump())

@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(
    nome: Optional[str] = None, 
    db: Session = Depends(get_db)
    ):
    return cliente_service.listar_clientes(db, nome)

@router.get("/{cliente_id}", response_model=ClienteResponse)
def buscar_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db)
    ):
    return cliente_service.buscar_cliente(db, cliente_id)

@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(
    cliente_id: int, 
    dados: ClienteCreate, 
    db: Session = Depends(get_db)
):
    cliente = cliente_service.buscar_cliente(db, cliente_id)
    return cliente_service.atualizar_cliente(db, cliente, dados.model_dump())

@router.delete("/{cliente_id}")
def remover_cliente(
    cliente_id: int, 
    db: Session = Depends(get_db)
):
    cliente = cliente_service.buscar_cliente(db, cliente_id)
    cliente_service.remover_cliente(db, cliente)
    return {"mensagem": "Cliente removido com sucesso"}