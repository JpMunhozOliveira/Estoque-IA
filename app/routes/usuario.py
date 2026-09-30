from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse
from app.services import usuario as usuario_service
from app.auth import usuario_atual

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.criar_usuario(db, usuario.nome, usuario.login, usuario.senha, usuario.papel)

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(nome: Optional[str] = None, db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db, nome)

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.delete("/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    usuario_service.remover_usuario(db, usuario, atual)
    return {"mensagem": "Usuário removido com sucesso"}