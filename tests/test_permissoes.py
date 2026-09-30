import pytest

ENTIDADES = ["produtos", "fornecedores", "clientes"]
SO_GESTOR = [(m, f"/{e}{s}") for e in ENTIDADES for m, s in
             [("POST", "/"), ("PUT", "/1"), ("DELETE", "/1"), ("POST", "/novo"),
              ("GET", "/1/editar"), ("POST", "/1/editar"), ("POST", "/1/remover")]]
SO_GESTOR += [("POST", "/usuarios/"), ("DELETE", "/usuarios/1"), ("POST", "/usuarios/novo"),
              ("POST", "/usuarios/1/remover"), ("GET", "/usuarios/1/redefinir-senha"),
              ("POST", "/usuarios/1/redefinir-senha"),
              ("GET", "/backups/pagina"), ("POST", "/backups/gerar"), ("POST", "/backups/restaurar"),
              ("POST", "/backups/enviar"), ("GET", "/backups/x.sql/download")]

LEITURAS = ["/produtos/pagina", "/fornecedores/pagina", "/clientes/pagina", "/usuarios/pagina",
            "/movimentacoes/pagina", "/usuarios/minha-senha",
            "/produtos/", "/fornecedores/", "/clientes/", "/usuarios/", "/movimentacoes/"]


@pytest.mark.parametrize("metodo,caminho", SO_GESTOR)
def test_operador_bloqueado(operador, metodo, caminho):
    assert operador.request(metodo, caminho, json={}).status_code == 403


@pytest.mark.parametrize("metodo,caminho", SO_GESTOR)
def test_anonimo_bloqueado(anonimo, metodo, caminho):
    assert anonimo.request(metodo, caminho, json={}).status_code == 401


@pytest.mark.parametrize("caminho", LEITURAS + ["/"])
def test_anonimo_nao_le_nada(anonimo, caminho):
    assert anonimo.get(caminho).status_code == 401      # "/" provavelmente falha: veja achados


@pytest.mark.parametrize("caminho", LEITURAS)
def test_operador_e_gestor_leem(operador, gestor, caminho):
    assert operador.get(caminho).status_code == 200
    assert gestor.get(caminho).status_code == 200


def test_anonimo_html_redireciona_para_login(anonimo):
    r = anonimo.get("/produtos/pagina", headers={"accept": "text/html"})
    assert r.status_code == 303 and r.headers["location"] == "/login"


def test_ui_esconde_acoes_do_operador(operador, gestor, make_produto):
    make_produto()
    assert "Novo produto" not in operador.get("/produtos/pagina").text
    assert "Novo produto" in gestor.get("/produtos/pagina").text
    assert "/backups/pagina" not in operador.get("/usuarios/pagina").text
    assert "/backups/pagina" in gestor.get("/usuarios/pagina").text


def test_cookie_forjado(anonimo):
    anonimo.cookies.set("session", "lixo")
    assert anonimo.get("/produtos/pagina").status_code == 401


def test_sessao_de_usuario_removido_perde_acesso(gestor, operador):
    assert gestor.delete(f"/usuarios/{operador.usuario_id}").status_code == 200
    assert operador.get("/produtos/pagina").status_code == 401


def test_gestor_nao_remove_a_si_mesmo(gestor):
    assert gestor.delete(f"/usuarios/{gestor.usuario_id}").status_code == 409