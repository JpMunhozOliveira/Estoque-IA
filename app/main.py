from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import engine, Base
from app.models import Produto, Fornecedor, Cliente, Usuario, Movimentacao
from app.routes.produto import router as produto_router
from app.routes.web.produto import router as produto_web_router
from app.routes.fornecedor import router as fornecedor_router
from app.routes.cliente import router as cliente_router
from app.routes.usuario import router as usuario_router
from app.routes.movimentacao import router as movimentacao_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(produto_router)
app.include_router(produto_web_router)
app.include_router(fornecedor_router)
app.include_router(cliente_router)
app.include_router(usuario_router)
app.include_router(movimentacao_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root():
    return RedirectResponse(url="/produtos/pagina")