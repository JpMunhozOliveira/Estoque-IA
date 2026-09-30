from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioResponse
from app.services import usuario as usuario_service
from app.auth import usuario_atual
from app.exceptions import RegraDeNegocioError

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

def _conferir_confirmacao(nova: str, confirmar: str):
    if nova != confirmar:
        raise RegraDeNegocioError("A confirmação não confere com a nova senha.", status_code=400)

@router.get("/minha-senha")
def pagina_minha_senha(request: Request):
    return templates.TemplateResponse(request, "minha_senha.html", {})

@router.post("/minha-senha")
def alterar_minha_senha(
    senha_atual: str = Form(...), nova_senha: str = Form(...), confirmar: str = Form(...),
    db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)
):
    _conferir_confirmacao(nova_senha, confirmar)
    usuario_service.alterar_senha(db, atual, senha_atual, nova_senha)
    return RedirectResponse(url="/", status_code=303)

@router.get("/{usuario_id}/redefinir-senha")
def pagina_redefinir_senha(usuario_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    return templates.TemplateResponse(request, "redefinir_senha.html", {"usuario": usuario})

@router.post("/{usuario_id}/redefinir-senha")
def redefinir_senha_salvar(
    usuario_id: int, nova_senha: str = Form(...), confirmar: str = Form(...),
    db: Session = Depends(get_db)
):
    _conferir_confirmacao(nova_senha, confirmar)
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    usuario_service.redefinir_senha(db, usuario, nova_senha)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)