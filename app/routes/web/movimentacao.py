from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.models import Produto, Usuario, Cliente
from app.services import movimentacao as movimentacao_service

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações - Web"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pagina")
def pagina_movimentacoes(request: Request, db: Session = Depends(get_db)):
    movimentacoes = movimentacao_service.listar_movimentacoes(db)
    produtos = db.query(Produto).all()
    usuarios = db.query(Usuario).all()
    clientes = db.query(Cliente).all()
    return templates.TemplateResponse(request, "movimentacoes.html", {
        "movimentacoes": movimentacoes,
        "produtos": produtos,
        "usuarios": usuarios,
        "clientes": clientes
    })

@router.post("/nova")
def criar_movimentacao_form(
    produto_id: int = Form(...), usuario_id: int = Form(...),
    cliente_id: str = Form(""), tipo: str = Form(...),
    quantidade: float = Form(...), valor_unitario: float = Form(0),
    db: Session = Depends(get_db)
):
    dados = {
        "produto_id": produto_id, "usuario_id": usuario_id,
        "cliente_id": int(cliente_id) if cliente_id else None,
        "tipo": tipo, "quantidade": quantidade, "valor_unitario": valor_unitario
    }
    movimentacao_service.criar_movimentacao(db, dados)
    return RedirectResponse(url="/movimentacoes/pagina", status_code=303)