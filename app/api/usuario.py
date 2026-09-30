from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Optional
from app.db.database import get_db
from app.core.auth import usuario_atual
from app.models.models import Usuario
from app.schemas.schemas import UsuarioCreate, UsuarioResponse
from app.services import usuario as usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.post("/", response_model=UsuarioResponse)
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    return usuario_service.criar_usuario(db, usuario.nome, usuario.login, usuario.senha, usuario.papel)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    nome: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return usuario_service.listar_usuarios(db, nome)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db)
):
    return usuario_service.buscar_usuario(db, usuario_id)

@router.delete("/{usuario_id}")
def remover_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    atual: Usuario = Depends(usuario_atual),
):
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    usuario_service.remover_usuario(db, usuario, atual)
    return {"mensagem": "Usuário removido com sucesso"}
