import os
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.models import Usuario, Movimentacao
from app.schemas.schemas import UsuarioCreate, SenhaNova
from app.core.exceptions import RegraDeNegocioError, validar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Usado quando o login não existe, para o tempo de resposta não revelar quais logins existem
_HASH_FALSO = pwd_context.hash("senha-falsa")

_MSG_LOGIN_DUPLICADO = "Já existe um usuário com esse login."

def criar_usuario(db: Session, nome: str, login: str, senha: str, papel: str = "operador") -> Usuario:
    dados = validar(UsuarioCreate, {"nome": nome.strip(), "login": login.strip(), "senha": senha, "papel": papel})

    if db.query(Usuario).filter(Usuario.login == dados.login).first():
        raise RegraDeNegocioError(_MSG_LOGIN_DUPLICADO, status_code=409)

    novo = Usuario(nome=dados.nome, login=dados.login, papel=dados.papel,
                   senha_hash=pwd_context.hash(dados.senha))
    db.add(novo)
    try:
        db.commit()
    except IntegrityError:
        # Corrida: dois cadastros do mesmo login ao mesmo tempo (a constraint UNIQUE segura)
        db.rollback()
        raise RegraDeNegocioError(_MSG_LOGIN_DUPLICADO, status_code=409)
    db.refresh(novo)
    return novo

def autenticar(db: Session, login: str, senha: str) -> Optional[Usuario]:
    if "\x00" in login or "\x00" in senha:
        pwd_context.verify("x", _HASH_FALSO)   # mantém o tempo de resposta parecido
        return None
    
    usuario = db.query(Usuario).filter(Usuario.login == login.strip()).first()
    senha_ok = pwd_context.verify(senha, usuario.senha_hash if usuario else _HASH_FALSO)
    return usuario if (usuario and senha_ok) else None

def listar_usuarios(db: Session, nome: Optional[str] = None):
    query = db.query(Usuario)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    return query.order_by(Usuario.nome).all()

def remover_usuario(db: Session, usuario: Usuario, executor: Optional[Usuario] = None):
    if executor and executor.id == usuario.id:
        raise RegraDeNegocioError("Você não pode remover o seu próprio usuário.", status_code=409)
    total = db.query(Movimentacao).filter(Movimentacao.usuario_id == usuario.id).count()
    if total:
        raise RegraDeNegocioError(
            f"Não é possível remover: o usuário possui {total} movimentação(ões) registrada(s).",
            status_code=409,
        )
    db.delete(usuario)
    db.commit()

def criar_gestor_inicial(db: Session):
    """Se não existir nenhum gestor, cria um a partir de ADMIN_LOGIN / ADMIN_SENHA."""
    if db.query(Usuario).filter(Usuario.papel == "gestor").first():
        return
    login, senha = os.getenv("ADMIN_LOGIN"), os.getenv("ADMIN_SENHA")
    if not login or not senha:
        print("AVISO: não há gestor cadastrado e ADMIN_LOGIN/ADMIN_SENHA não foram definidos.")
        return
    criar_usuario(db, "Administrador", login, senha, "gestor")

def buscar_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise RegraDeNegocioError("Usuário não encontrado", status_code=404)
    return usuario

def _definir_senha(db: Session, usuario: Usuario, nova_senha: str):
    dados = validar(SenhaNova, {"senha": nova_senha})
    usuario.senha_hash = pwd_context.hash(dados.senha)
    db.commit()

def alterar_senha(db: Session, usuario: Usuario, senha_atual: str, nova_senha: str):
    if not pwd_context.verify(senha_atual, usuario.senha_hash):
        raise RegraDeNegocioError("Senha atual incorreta.", status_code=400)
    _definir_senha(db, usuario, nova_senha)

def redefinir_senha(db: Session, usuario: Usuario, nova_senha: str):
    _definir_senha(db, usuario, nova_senha)