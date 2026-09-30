from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import usuario as usuario_service

router = APIRouter(tags=["Autenticação"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login")
def pagina_login(request: Request):
    if request.session.get("usuario_id"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request, "auth/login.html", {"erro": None})

@router.post("/login")
def entrar(request: Request, login: str = Form(...), senha: str = Form(...), db: Session = Depends(get_db)):
    usuario = usuario_service.autenticar(db, login, senha)
    if not usuario:
        return templates.TemplateResponse(request, "auth/login.html", {"erro": "Login ou senha inválidos"}, status_code=401)
    request.session.clear()
    request.session.update({"usuario_id": usuario.id, "usuario_nome": usuario.nome, "papel": usuario.papel})
    return RedirectResponse(url="/", status_code=303)

@router.post("/logout")
def sair(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)