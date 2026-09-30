from decimal import Decimal
from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.database import SessionLocal
from app.services import movimentacao as movimentacao_service
from app.auth import usuario_atual
from app.models import Produto, Usuario, Cliente

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
    return templates.TemplateResponse(request, "movimentacoes.html", {
        "movimentacoes": movimentacao_service.listar_movimentacoes(db),
        "produtos": db.query(Produto).order_by(Produto.nome).all(),
        "clientes": db.query(Cliente).order_by(Cliente.nome).all(),
    })

@router.post("/nova")
def criar_movimentacao_form(
    produto_id: int = Form(...), cliente_id: str = Form(""), tipo: str = Form(...),
    quantidade: Decimal = Form(...), valor_unitario: Decimal = Form(Decimal("0")),
    db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)
):
    dados = {
        "produto_id": produto_id, "cliente_id": int(cliente_id) if cliente_id else None,
        "tipo": tipo, "quantidade": quantidade, "valor_unitario": valor_unitario,
    }
    movimentacao_service.criar_movimentacao(db, dados, usuario.id)
    return RedirectResponse(url="/movimentacoes/pagina", status_code=303)