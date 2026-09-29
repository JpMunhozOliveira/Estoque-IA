from decimal import Decimal
from fastapi import Request, Form, APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Produto, Fornecedor
from app.services import produto as produto_service

router = APIRouter(prefix="/produtos", tags=["Produtos - Web"])
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda, fornecedor_id):
    # Sem "quantidade": o estoque só muda por Movimentação
    return {
        "nome": nome, "categoria": categoria, "unidade": unidade,
        "estoque_minimo": estoque_minimo,
        "preco_custo": preco_custo, "preco_venda": preco_venda,
        "fornecedor_id": int(fornecedor_id) if fornecedor_id else None
    }

@router.get("/pagina")
def pagina_produtos(request: Request, db: Session = Depends(get_db)):
    produtos = produto_service.listar_produtos(db)
    fornecedores = db.query(Fornecedor).all()
    return templates.TemplateResponse(request, "produtos.html", {
        "produtos": produtos,
        "fornecedores": fornecedores
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
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    fornecedores = db.query(Fornecedor).all()
    return templates.TemplateResponse(request, "editar_produto.html", {
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
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    dados = _dados_form(nome, categoria, unidade, estoque_minimo, preco_custo, preco_venda, fornecedor_id)
    produto_service.atualizar_produto(db, produto, dados)
    return RedirectResponse(url="/produtos/pagina", status_code=303)

@router.post("/{produto_id}/remover")
def remover_produto_form(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto:
        produto_service.remover_produto(db, produto)
    return RedirectResponse(url="/produtos/pagina", status_code=303)
