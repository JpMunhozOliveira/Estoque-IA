from decimal import Decimal
from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Fornecedor
from app.services import produto as produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos - Web"])
templates = Jinja2Templates(directory="app/templates")


def _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda, fornecedor_id):
    # Sem "quantidade": o estoque só muda por Movimentação
    return {
        "nome": nome, "categoria": categoria, "unidade": unidade,
        "estoque_minimo": estoque_minimo,
        "preco_custo": preco_custo, "preco_venda": preco_venda,
        "fornecedor_id": int(fornecedor_id) if fornecedor_id else None
    }

@router.get("/pagina")
def pagina_produtos(request: Request, abaixo_minimo: bool = False, db: Session = Depends(get_db)):
    produtos = produto_service.listar_produtos(db, abaixo_minimo=abaixo_minimo)
    fornecedores = db.query(Fornecedor).all()
    return templates.TemplateResponse(request, "produtos/produtos.html", {
        "produtos": produtos, "fornecedores": fornecedores, "abaixo_minimo": abaixo_minimo,
    })

@router.post("/novo")
def criar_produto_form(
    nome: str = Form(...), categoria: str = Form(""),
    unidade: str = Form("unidade"), estoque_minimo: Decimal = Form(Decimal("0")),
    preco_custo: Decimal = Form(Decimal("0")), preco_venda: Decimal = Form(Decimal("0")),
    fornecedor_id: str = Form(""), db: Session = Depends(get_db)
):
    dados = _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda, fornecedor_id)
    produto_service.criar_produto(db, dados)
    return RedirectResponse(url="/produtos/pagina", status_code=303)

@router.get("/{produto_id}/editar")
def editar_produto_form(produto_id: int, request: Request, db: Session = Depends(get_db)):
    produto = produto_service.buscar_produto(db, produto_id)
    fornecedores = db.query(Fornecedor).all()
    return templates.TemplateResponse(request, "produtos/editar_produto.html", {
        "produto": produto,
        "fornecedores": fornecedores
    })

@router.post("/{produto_id}/editar")
def editar_produto_salvar(
    produto_id: int,
    nome: str = Form(...), categoria: str = Form(""),
    unidade: str = Form("unidade"), estoque_minimo: Decimal = Form(Decimal("0")),
    preco_custo: Decimal = Form(Decimal("0")), preco_venda: Decimal = Form(Decimal("0")),
    fornecedor_id: str = Form(""), db: Session = Depends(get_db)
):
    produto = produto_service.buscar_produto(db, produto_id)
    dados = _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda, fornecedor_id)
    produto_service.atualizar_produto(db, produto, dados)
    return RedirectResponse(url="/produtos/pagina", status_code=303)

@router.post("/{produto_id}/remover")
def remover_produto_form(produto_id: int, db: Session = Depends(get_db)):
    produto = produto_service.buscar_produto(db, produto_id)
    produto_service.remover_produto(db, produto)
    return RedirectResponse(url="/produtos/pagina", status_code=303)
