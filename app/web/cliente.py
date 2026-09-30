from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import cliente as cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes - Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/pagina")
def pagina_clientes(request: Request, db: Session = Depends(get_db)):
    clientes = cliente_service.listar_clientes(db)
    return templates.TemplateResponse(request, "clientes/clientes.html", {"clientes": clientes})

@router.post("/novo")
def criar_cliente_form(nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    cliente_service.criar_cliente(db, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/clientes/pagina", status_code=303)

@router.get("/{cliente_id}/editar")
def editar_cliente_form(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    cliente = cliente_service.buscar_cliente(db, cliente_id)
    return templates.TemplateResponse(request, "clientes/editar_cliente.html", {"cliente": cliente})

@router.post("/{cliente_id}/editar")
def editar_cliente_salvar(cliente_id: int, nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    cliente = cliente_service.buscar_cliente(db, cliente_id)
    cliente_service.atualizar_cliente(db, cliente, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/clientes/pagina", status_code=303)

@router.post("/{cliente_id}/remover")
def remover_cliente_form(cliente_id: int, db: Session = Depends(get_db)):
    cliente = cliente_service.buscar_cliente(db, cliente_id)
    cliente_service.remover_cliente(db, cliente)
    return RedirectResponse(url="/clientes/pagina", status_code=303)