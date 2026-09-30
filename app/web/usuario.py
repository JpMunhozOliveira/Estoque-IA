from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import usuario as usuario_service
from app.core.auth import usuario_atual
from app.core.exceptions import RegraDeNegocioError
from app.models.models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuários - Web"])
templates = Jinja2Templates(directory="app/templates")

def _conferir_confirmacao(nova: str, confirmar: str):
    if nova != confirmar:
        raise RegraDeNegocioError(
            "A confirmação não confere com a nova senha.",
            status_code=400,
        )

@router.get("/pagina")
def pagina_usuarios(request: Request, db: Session = Depends(get_db)):
    usuarios = usuario_service.listar_usuarios(db)
    return templates.TemplateResponse(request, "usuarios/index.html", {"usuarios": usuarios})

@router.post("/novo")
def criar_usuario_form(
    nome: str = Form(...), login: str = Form(...), senha: str = Form(...),
    papel: str = Form("operador"), db: Session = Depends(get_db)
):
    usuario_service.criar_usuario(db, nome, login, senha, papel)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)

@router.post("/{usuario_id}/remover")
def remover_usuario_form(usuario_id: int, db: Session = Depends(get_db), atual: Usuario = Depends(usuario_atual)):
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    usuario_service.remover_usuario(db, usuario, atual)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)

@router.get("/minha-senha")
def pagina_minha_senha(request: Request):
    return templates.TemplateResponse(request, "usuarios/minha_senha.html", {})


@router.post("/minha-senha")
def alterar_minha_senha(
    senha_atual: str = Form(...),
    nova_senha: str = Form(...),
    confirmar: str = Form(...),
    db: Session = Depends(get_db),
    atual: Usuario = Depends(usuario_atual),
):
    _conferir_confirmacao(nova_senha, confirmar)
    usuario_service.alterar_senha(db, atual, senha_atual, nova_senha)
    return RedirectResponse(url="/", status_code=303)


@router.get("/{usuario_id}/redefinir-senha")
def pagina_redefinir_senha(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    return templates.TemplateResponse(
        request,
        "usuarios/redefinir_senha.html",
        {"usuario": usuario},
    )


@router.post("/{usuario_id}/redefinir-senha")
def redefinir_senha_salvar(
    usuario_id: int,
    nova_senha: str = Form(...),
    confirmar: str = Form(...),
    db: Session = Depends(get_db),
):
    _conferir_confirmacao(nova_senha, confirmar)
    usuario = usuario_service.buscar_usuario(db, usuario_id)
    usuario_service.redefinir_senha(db, usuario, nova_senha)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)