from fastapi import Request, Form, APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import SessionLocal
from app.models.models import Fornecedor
from app.services import fornecedor as fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores - Web"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pagina")
def pagina_fornecedores(request: Request, db: Session = Depends(get_db)):
    fornecedores = fornecedor_service.listar_fornecedores(db)
    return templates.TemplateResponse(request, "fornecedores/fornecedores.html", {"fornecedores": fornecedores})

@router.post("/novo")
def criar_fornecedor_form(nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    fornecedor_service.criar_fornecedor(db, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/fornecedores/pagina", status_code=303)

@router.get("/{fornecedor_id}/editar")
def editar_fornecedor_form(fornecedor_id: int, request: Request, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return templates.TemplateResponse(request, "fornecedores/editar_fornecedor.html", {"fornecedor": fornecedor})

@router.post("/{fornecedor_id}/editar")
def editar_fornecedor_salvar(fornecedor_id: int, nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    fornecedor_service.atualizar_fornecedor(db, fornecedor, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/fornecedores/pagina", status_code=303)

@router.post("/{fornecedor_id}/remover")
def remover_fornecedor_form(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if fornecedor:
        fornecedor_service.remover_fornecedor(db, fornecedor)
    return RedirectResponse(url="/fornecedores/pagina", status_code=303)