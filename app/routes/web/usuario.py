from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import usuario as usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários - Web"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pagina")
def pagina_usuarios(request: Request, db: Session = Depends(get_db)):
    usuarios = usuario_service.listar_usuarios(db)
    return templates.TemplateResponse(request, "usuarios.html", {"usuarios": usuarios})

@router.post("/novo")
def criar_usuario_form(
    nome: str = Form(...), login: str = Form(...), senha: str = Form(...),
    papel: str = Form("operador"), db: Session = Depends(get_db)
):
    usuario_service.criar_usuario(db, nome, login, senha, papel)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)

@router.post("/{usuario_id}/remover")
def remover_usuario_form(usuario_id: int, db: Session = Depends(get_db)):
    from app.models import Usuario
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario:
        usuario_service.remover_usuario(db, usuario)
    return RedirectResponse(url="/usuarios/pagina", status_code=303)