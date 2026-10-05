from decimal import Decimal
from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.auth import usuario_atual
from app.services import movimentacao as movimentacao_service
from app.models.models import Produto, Usuario, Cliente, Fornecedor

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações - Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/pagina")
def pagina_movimentacoes(
    request: Request, 
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse(request, "movimentacoes/index.html", {
        "movimentacoes": movimentacao_service.listar_movimentacoes(db),
        "produtos": db.query(Produto).order_by(Produto.nome).all(),
        "clientes": db.query(Cliente).order_by(Cliente.nome).all(),
        "fornecedores": db.query(Fornecedor).order_by(Fornecedor.nome).all(),
    })

@router.post("/nova")
def criar_movimentacao_form(
    produto_id: int = Form(...), 
    cliente_id: str = Form(""), 
    fornecedor_id: str = Form(""),
    tipo: str = Form(...), 
    quantidade: Decimal = Form(...),
    valor_unitario: Decimal = Form(Decimal("0")),
    documento: str = Form(""), 
    observacao: str = Form(""), 
    motivo_ajuste: str = Form(""),
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(usuario_atual)
):
    dados = {
        "produto_id": produto_id,
        "cliente_id": int(cliente_id) if cliente_id else None,
        "fornecedor_id": int(fornecedor_id) if fornecedor_id else None,
        "tipo": tipo, "quantidade": quantidade, "valor_unitario": valor_unitario,
        "documento": documento.strip() or None,
        "observacao": observacao.strip() or None,
        "motivo_ajuste": motivo_ajuste or None,
    }
    movimentacao_service.criar_movimentacao(db, dados, usuario.id)
    return RedirectResponse(url="/movimentacoes/pagina", status_code=303)