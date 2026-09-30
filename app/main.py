from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from app.auth import controle_de_acesso, usuario_atual
from app.config import SECRET_KEY
from app.database import SessionLocal
from app.exceptions import RegraDeNegocioError, NaoAutenticadoError
from app.services import usuario as usuario_service
from app.routes.produto import router as produto_router
from app.routes.fornecedor import router as fornecedor_router
from app.routes.cliente import router as cliente_router
from app.routes.usuario import router as usuario_router
from app.routes.movimentacao import router as movimentacao_router
from app.routes.web.auth import router as auth_web_router
from app.routes.web.produto import router as produto_web_router
from app.routes.web.fornecedor import router as fornecedor_web_router
from app.routes.web.cliente import router as cliente_web_router
from app.routes.web.usuario import router as usuario_web_router
from app.routes.web.movimentacao import router as movimentacao_web_router

# As tabelas são criadas e alteradas só pelo Alembic (alembic upgrade head).


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        usuario_service.criar_gestor_inicial(db)
    yield


app = FastAPI(lifespan=lifespan)
# em produção com HTTPS, acrescente https_only=True
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=60 * 60 * 8, same_site="lax")
templates = Jinja2Templates(directory="app/templates")


def _quer_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")


@app.exception_handler(RegraDeNegocioError)
def tratar_regra_de_negocio(request: Request, erro: RegraDeNegocioError):
    if _quer_html(request):
        return templates.TemplateResponse(
            request, "erro.html", {"mensagem": erro.mensagem}, status_code=erro.status_code
        )
    return JSONResponse(status_code=erro.status_code, content={"detail": erro.mensagem})


@app.exception_handler(NaoAutenticadoError)
def tratar_nao_autenticado(request: Request, erro: NaoAutenticadoError):
    if _quer_html(request):
        return RedirectResponse(url="/login", status_code=303)
    return JSONResponse(status_code=401, content={"detail": "Não autenticado"})


# /login e /logout são os únicos sem proteção
app.include_router(auth_web_router)

protegido = [Depends(controle_de_acesso)]
for r in (
    produto_web_router, fornecedor_web_router, cliente_web_router, usuario_web_router,
    movimentacao_web_router, produto_router, fornecedor_router, cliente_router,
    usuario_router, movimentacao_router,
):
    app.include_router(r, dependencies=protegido)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def read_root(request: Request, usuario=Depends(usuario_atual)):
    return templates.TemplateResponse(request, "index.html", {})