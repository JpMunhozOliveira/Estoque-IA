from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.exceptions import RegraDeNegocioError
from app.routes.produto import router as produto_router
from app.routes.fornecedor import router as fornecedor_router
from app.routes.cliente import router as cliente_router
from app.routes.usuario import router as usuario_router
from app.routes.movimentacao import router as movimentacao_router
from app.routes.web.produto import router as produto_web_router
from app.routes.web.fornecedor import router as fornecedor_web_router
from app.routes.web.cliente import router as cliente_web_router
from app.routes.web.usuario import router as usuario_web_router
from app.routes.web.movimentacao import router as movimentacao_web_router

# As tabelas são criadas e alteradas só pelo Alembic (alembic upgrade head).
# Não usamos mais Base.metadata.create_all aqui.

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(RegraDeNegocioError)
def tratar_regra_de_negocio(request: Request, erro: RegraDeNegocioError):
    # Navegador (formulários HTML) recebe uma página de erro; API/Swagger recebe JSON
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            request, "erro.html", {"mensagem": erro.mensagem}, status_code=erro.status_code
        )
    return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})


app.include_router(produto_web_router)
app.include_router(fornecedor_web_router)
app.include_router(cliente_web_router)
app.include_router(usuario_web_router)
app.include_router(movimentacao_web_router)
app.include_router(produto_router)
app.include_router(fornecedor_router)
app.include_router(cliente_router)
app.include_router(usuario_router)
app.include_router(movimentacao_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})
