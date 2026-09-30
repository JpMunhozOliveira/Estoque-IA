from fastapi import Request, Form, APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import SessionLocal
from app.models.models import Cliente
from app.services import cliente as cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes - Web"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="cliente não encontrado")
    return templates.TemplateResponse(request, "clientes/editar_cliente.html", {"cliente": cliente})

@router.post("/{cliente_id}/editar")
def editar_cliente_salvar(cliente_id: int, nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="cliente não encontrado")
    cliente_service.atualizar_cliente(db, cliente, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/clientes/pagina", status_code=303)

@router.post("/{cliente_id}/remover")
def remover_cliente_form(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        cliente_service.remover_cliente(db, cliente)
    return RedirectResponse(url="/clientes/pagina", status_code=303)