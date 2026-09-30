from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import fornecedor as fornecedor_service

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores - Web"])
templates = Jinja2Templates(directory="app/templates")


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
    fornecedor = fornecedor_service.buscar_fornecedor(db, fornecedor_id)
    return templates.TemplateResponse(request, "fornecedores/editar_fornecedor.html", {"fornecedor": fornecedor})

@router.post("/{fornecedor_id}/editar")
def editar_fornecedor_salvar(fornecedor_id: int, nome: str = Form(...), contato: str = Form(""), db: Session = Depends(get_db)):
    fornecedor = fornecedor_service.buscar_fornecedor(db, fornecedor_id)
    fornecedor_service.atualizar_fornecedor(db, fornecedor, {"nome": nome, "contato": contato})
    return RedirectResponse(url="/fornecedores/pagina", status_code=303)

@router.post("/{fornecedor_id}/remover")
def remover_fornecedor_form(fornecedor_id: int, db: Session = Depends(get_db)):
    fornecedor = fornecedor_service.buscar_fornecedor(db, fornecedor_id)
    fornecedor_service.remover_fornecedor(db, fornecedor)
    return RedirectResponse(url="/fornecedores/pagina", status_code=303)