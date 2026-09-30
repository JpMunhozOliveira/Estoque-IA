import subprocess
from decimal import Decimal

import pytest

from app.core.exceptions import RegraDeNegocioError
from app.models.models import Usuario
from app.services import backup as backup_service
from app.services import usuario as usuario_service


def test_login_com_nul_retorna_401(anonimo):
    r = anonimo.post("/login", data={"login": "a\x00", "senha": "x"})
    assert r.status_code == 401


def test_login_logado_redireciona(gestor):
    r = gestor.get("/login")
    assert r.status_code == 303 and r.headers["location"] == "/"


def test_gestor_inicial(db, monkeypatch):
    monkeypatch.setenv("ADMIN_LOGIN", "chefe")
    monkeypatch.setenv("ADMIN_SENHA", "abcdef")
    usuario_service.criar_gestor_inicial(db)
    assert db.query(Usuario).filter_by(login="chefe", papel="gestor").count() == 1
    usuario_service.criar_gestor_inicial(db)            # idempotente
    assert db.query(Usuario).filter_by(papel="gestor").count() == 1


def test_gestor_inicial_sem_variaveis(db, monkeypatch, capsys):
    monkeypatch.delenv("ADMIN_LOGIN", raising=False)
    monkeypatch.delenv("ADMIN_SENHA", raising=False)
    usuario_service.criar_gestor_inicial(db)
    assert db.query(Usuario).count() == 0
    assert "AVISO" in capsys.readouterr().out


def test_paginas_web_diversas(gestor, operador, make_produto):
    p = make_produto()
    assert gestor.get(f"/produtos/{p.id}/editar").status_code == 200
    assert gestor.get(f"/usuarios/{operador.usuario_id}/redefinir-senha").status_code == 200
    assert gestor.get("/usuarios/99999/redefinir-senha").status_code == 404
    assert gestor.form("/usuarios/99999/redefinir-senha",
                       nova_senha="abcdef", confirmar="abcdef").status_code == 404
    assert gestor.get("/usuarios/", params={"nome": "oper"}).json()[0]["login"] == "operador"


def test_nul_em_json(gestor):
    r = gestor.post("/clientes/", content=b'{"nome": "a\\u0000b"}',
                    headers={"content-type": "application/json"})
    assert r.status_code == 422


def test_listar_backups_vazio_e_com_arquivo(gestor):
    assert backup_service.listar_backups() is not None
    gestor.form("/backups/gerar")
    assert len(backup_service.listar_backups()) >= 1
    assert "estoque_" in gestor.get("/backups/pagina").text


def test_backup_timeout_e_erro(monkeypatch):
    def timeout(*a, **k):
        raise subprocess.TimeoutExpired("pg_dump", 1)

    def falha(*a, **k):
        raise subprocess.CalledProcessError(1, "pg_dump")

    for func in (backup_service.criar_backup,):
        monkeypatch.setattr(subprocess, "run", timeout)
        with pytest.raises(RegraDeNegocioError) as e:
            func()
        assert e.value.status_code == 504
        monkeypatch.setattr(subprocess, "run", falha)
        with pytest.raises(RegraDeNegocioError) as e:
            func()
        assert e.value.status_code == 500


def test_restaurar_timeout_e_erro(gestor, monkeypatch):
    gestor.form("/backups/gerar")
    nome = backup_service.listar_backups()[0]["nome"]

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(
        subprocess.TimeoutExpired("psql", 1)))
    with pytest.raises(RegraDeNegocioError) as e:
        backup_service.restaurar_backup(nome)
    assert e.value.status_code == 504

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(
        subprocess.CalledProcessError(1, "psql")))
    with pytest.raises(RegraDeNegocioError) as e:
        backup_service.restaurar_backup(nome)
    assert e.value.status_code == 500


def test_upload_acima_do_limite(gestor, monkeypatch):
    from app.web import backup as web_backup
    monkeypatch.setattr(web_backup, "BACKUP_MAX_SIZE_MB", 0)
    r = gestor.post("/backups/enviar", data={"csrf_token": gestor.csrf},
                    files={"arquivo": ("x.sql", b"-- PostgreSQL database dump")})
    assert r.status_code == 413


def test_backup_inexistente(gestor):
    assert gestor.get("/backups/nao_existe.sql/download").status_code == 404