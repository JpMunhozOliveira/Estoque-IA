from decimal import Decimal
from fastapi import Request, Form, APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Fornecedor
from app.services import produto as produto_service
from app.core.formatacao import parse_reais
from app.core.templates import templates

router = APIRouter(prefix="/produtos", tags=["Produtos - Web"])

def _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda):
    # Sem "quantidade" (só muda por Movimentação) e sem fornecedor (vem das entradas)
    return {
        "nome": nome, "categoria": categoria, "unidade": unidade,
        "estoque_minimo": estoque_minimo,
        "preco_custo": parse_reais(preco_custo, "Preço de custo"),
        "preco_venda": parse_reais(preco_venda, "Preço de venda"),
    }

@router.get("/pagina")
def pagina_produtos(request: Request, abaixo_minimo: bool = False, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "produtos/produtos.html", {
        "produtos": produto_service.listar_produtos(db, abaixo_minimo=abaixo_minimo),
        "fornecedores_por_produto": produto_service.fornecedores_por_produto(db),
        "abaixo_minimo": abaixo_minimo,
    })

@router.post("/novo")
def criar_produto_form(
    nome: str = Form(...), categoria: str = Form(""),
    unidade: str = Form("unidade"), estoque_minimo: Decimal = Form(Decimal("0")),
    preco_custo: str = Form("0"), preco_venda: str = Form("0"),
    db: Session = Depends(get_db),
):
    produto_service.criar_produto(
        db, _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda))
    return RedirectResponse(url="/produtos/pagina", status_code=303)

@router.get("/{produto_id}/editar")
def editar_produto_form(produto_id: int, request: Request, db: Session = Depends(get_db)):
    produto = produto_service.buscar_produto(db, produto_id)
    fornecedores = produto_service.fornecedores_por_produto(db).get(produto.id, [])
    return templates.TemplateResponse(request, "produtos/editar_produto.html", {
        "produto": produto, "fornecedores": fornecedores,
    })

@router.post("/{produto_id}/editar")
def editar_produto_salvar(
    produto_id: int,
    nome: str = Form(...), categoria: str = Form(""),
    unidade: str = Form("unidade"), estoque_minimo: Decimal = Form(Decimal("0")),
    preco_custo: str = Form("0"), preco_venda: str = Form("0"),
    db: Session = Depends(get_db),
):
    produto = produto_service.buscar_produto(db, produto_id)
    produto_service.atualizar_produto(
        db, produto, _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda))
    return RedirectResponse(url="/produtos/pagina", status_code=303)

@router.post("/{produto_id}/remover")
def remover_produto_form(produto_id: int, db: Session = Depends(get_db)):
    produto = produto_service.buscar_produto(db, produto_id)
    produto_service.remover_produto(db, produto)
    return RedirectResponse(url="/produtos/pagina", status_code=303)
