import os
import re
import tempfile
from decimal import Decimal

from dotenv import load_dotenv
load_dotenv()

# --- TEM que vir antes de importar o app (config.py lê o ambiente no import) ---
from sqlalchemy.engine import make_url
_url = make_url(os.environ["DATABASE_URL"]).set(database="estoque_test")  # nunca o banco real
os.environ["DATABASE_URL"] = _url.render_as_string(hide_password=False)
os.environ.setdefault("SECRET_KEY", "chave-so-para-testes")
os.environ["DOCS_ATIVAS"] = "false"
os.environ["BACKUP_DIR"] = tempfile.mkdtemp(prefix="backups_test_")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.database import SessionLocal, engine
from app.main import app
from app.models.models import Produto
from app.services import usuario as usuario_service
from app.services import produto as produto_service
from app.services import cliente as cliente_service
from app.services import fornecedor as fornecedor_service

usuario_service.pwd_context.update(bcrypt__rounds=4)  # hash rápido só nos testes
SENHA = "senha123"
os.environ["DOCS_ATIVAS"] = "false"

@pytest.fixture(scope="session", autouse=True)
def _schema():
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def _banco_limpo(_schema):
    with engine.begin() as conn:
        conn.execute(text(
            "TRUNCATE movimentacoes, produtos, fornecedores, clientes, usuarios "
            "RESTART IDENTITY CASCADE"))


@pytest.fixture
def db():
    with SessionLocal() as s:
        yield s


def _client():
    return TestClient(app, follow_redirects=False, raise_server_exceptions=False)


def _logado(db, login, papel):
    u = usuario_service.criar_usuario(db, login.capitalize(), login, SENHA, papel)
    c = _client()
    assert c.post("/login", data={"login": login, "senha": SENHA}).status_code == 303
    pagina = c.get("/usuarios/minha-senha")
    c.csrf = re.search(r'name="csrf_token" value="([^"]+)"', pagina.text).group(1)
    c.usuario_id = u.id
    c.form = lambda url, **dados: c.post(url, data={**dados, "csrf_token": c.csrf})
    return c


@pytest.fixture
def anonimo():
    return _client()

@pytest.fixture
def gestor(db):
    return _logado(db, "gestor", "gestor")

@pytest.fixture
def operador(db):
    return _logado(db, "operador", "operador")


@pytest.fixture
def make_produto(db):
    def _make(**kw):
        dados = {"nome": "Produto teste", "unidade": "un", "estoque_minimo": Decimal("0"),
                 "preco_custo": Decimal("1"), "preco_venda": Decimal("2")} | kw
        return produto_service.criar_produto(db, dados)
    return _make

@pytest.fixture
def make_cliente(db):
    return lambda nome="Cliente teste": cliente_service.criar_cliente(db, {"nome": nome, "contato": ""})

@pytest.fixture
def make_fornecedor(db):
    return lambda nome="Fornecedor teste": fornecedor_service.criar_fornecedor(db, {"nome": nome, "contato": ""})

@pytest.fixture
def estoque(db):
    def _q(produto_id):
        db.expire_all()  # o app commitou em outra sessão
        return db.get(Produto, produto_id).quantidade
    return _q