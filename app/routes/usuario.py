from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    senha_hash = pwd_context.hash(usuario.senha)
    novo = Usuario(
        nome=usuario.nome,
        login=usuario.login,
        papel=usuario.papel,
        senha_hash=senha_hash
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(nome: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Usuario)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    return query.all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def buscar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.delete("/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensagem": "Usuário removido com sucesso"}