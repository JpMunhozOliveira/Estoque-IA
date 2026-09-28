from sqlalchemy.orm import Session
from typing import Optional
from passlib.context import CryptContext
from app.models import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_usuario(db: Session, nome: str, login: str, senha: str, papel: str = "operador") -> Usuario:
    novo = Usuario(nome=nome, login=login, papel=papel, senha_hash=pwd_context.hash(senha))
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def listar_usuarios(db: Session, nome: Optional[str] = None):
    query = db.query(Usuario)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    return query.all()

def remover_usuario(db: Session, usuario: Usuario):
    db.delete(usuario)
    db.commit()