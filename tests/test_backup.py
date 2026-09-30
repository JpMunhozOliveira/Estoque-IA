import re
import shutil
from pathlib import Path

import pytest

from app.models.models import Produto

pytestmark = pytest.mark.skipif(not shutil.which("pg_dump"), reason="pg_dump não instalado")


def _gerar(gestor):
    r = gestor.form("/backups/gerar")
    assert r.status_code == 200 and b"PostgreSQL database dump" in r.content
    return re.search(r'filename="?([^";]+)', r.headers["content-disposition"]).group(1)


def test_nome_invalido_e_path_traversal(gestor):
    for nome in ["a.txt", "..%2F..%2Fetc%2Fpasswd", "%2e%2e/x.sql", ".oculto.sql"]:
        assert gestor.get(f"/backups/{nome}/download").status_code in (400, 404)


def test_upload_invalido(gestor):
    envia = lambda nome, conteudo: gestor.post(
        "/backups/enviar", data={"csrf_token": gestor.csrf}, files={"arquivo": (nome, conteudo)})
    assert envia("x.txt", b"-- PostgreSQL database dump").status_code == 422
    assert envia("x.sql", b"").status_code == 422
    assert envia("x.sql", b"DROP TABLE usuarios;").status_code == 422     # sem cabeçalho do pg_dump
    assert envia("x.sql", b"-- PostgreSQL database dump\x00").status_code == 422
    assert envia("x.sql", b"-- PostgreSQL database dump\nSELECT 1;").status_code == 303


def test_restaurar_desfaz_alteracoes(db, gestor, make_produto):
    make_produto(nome="Original")
    nome = _gerar(gestor)

    db.query(Produto).delete(); db.commit()
    assert gestor.get("/produtos/").json() == []

    assert gestor.form("/backups/restaurar", nome=nome, confirmar_nome="outro.sql").status_code == 400

    db.close()   # libera locks: senão o DROP TABLE do psql fica esperando esta sessão
    r = gestor.form("/backups/restaurar", nome=nome, confirmar_nome=nome)
    assert r.status_code == 303 and r.headers["location"] == "/login"
    assert gestor.get("/produtos/").status_code == 401          # sessão foi limpa

    assert gestor.post("/login", data={"login": "gestor", "senha": "senha123"}).status_code == 303
    assert [p["nome"] for p in gestor.get("/produtos/").json()] == ["Original"]