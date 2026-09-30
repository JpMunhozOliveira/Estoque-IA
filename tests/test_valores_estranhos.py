import pytest

TEXTOS = ["'; DROP TABLE produtos; --", "<script>alert(1)</script>", "  espaços  ",
          "日本語 🚀 ação", "a" * 5000, "\x00", "%s %d {0}", "../../etc/passwd"]
NUMEROS = ["-1", "abc", "", "NaN", "Infinity", "1e30", "9999999999999", "1.9999", None, [], {}]
IDS = [0, -1, 999999, 10**20, "abc", "1.5"]
BASE = {"nome": "P", "unidade": "un", "estoque_minimo": "0", "preco_custo": "1", "preco_venda": "1"}


@pytest.mark.parametrize("texto", TEXTOS)
@pytest.mark.parametrize("url", ["/clientes/", "/fornecedores/"])
def test_texto_estranho_nunca_gera_500(gestor, url, texto):
    r = gestor.post(url, json={"nome": texto, "contato": texto})
    assert r.status_code < 500
    if r.status_code == 200:
        assert r.json()["nome"] == texto.strip()     # guardou literalmente


@pytest.mark.parametrize("texto", TEXTOS)
def test_busca_com_texto_estranho(gestor, texto):
    for url in ("/produtos/", "/clientes/", "/fornecedores/", "/usuarios/"):
        assert gestor.get(url, params={"nome": texto}).status_code < 500


def test_xss_e_escapado_no_html(gestor, make_cliente):
    make_cliente("<script>alert(1)</script>")
    html = gestor.get("/clientes/pagina").text
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;" in html


@pytest.mark.parametrize("campo", ["estoque_minimo", "preco_custo", "preco_venda"])
@pytest.mark.parametrize("valor", NUMEROS)
def test_numero_invalido_produto(gestor, campo, valor):
    assert gestor.post("/produtos/", json={**BASE, campo: valor}).status_code == 422


@pytest.mark.parametrize("valor", IDS)
def test_ids_estranhos(gestor, valor):
    for metodo, url in [("PUT", f"/produtos/{valor}"), ("DELETE", f"/produtos/{valor}"),
                        ("GET", f"/clientes/{valor}"), ("GET", f"/usuarios/{valor}"),
                        ("DELETE", f"/fornecedores/{valor}")]:
        r = gestor.request(metodo, url, json=BASE if metodo == "PUT" else None)
        assert r.status_code in (404, 422), (metodo, url, r.status_code)


@pytest.mark.parametrize("lixo", ["abc", "1.5", "-", "99999999999999999999"])
def test_ids_estranhos_em_formularios_web(gestor, lixo):
    r = gestor.form("/produtos/novo", nome="X", categoria="", unidade="un", estoque_minimo="0",
                    preco_custo="0", preco_venda="0", fornecedor_id=lixo)
    assert r.status_code < 500
    r = gestor.form("/movimentacoes/nova", produto_id="1", cliente_id=lixo, tipo="entrada",
                    quantidade="1", valor_unitario="0")
    assert r.status_code < 500


def test_corpo_quebrado(gestor):
    r = gestor.post("/produtos/", content=b"{nao e json", headers={"content-type": "application/json"})
    assert r.status_code == 422
    assert gestor.post("/produtos/", json=[]).status_code == 422
    assert gestor.post("/produtos/", json=None).status_code == 422


@pytest.mark.parametrize("login", ["admin' OR '1'='1", "\x00", "a" * 10000])
def test_login_estranho(anonimo, gestor, login):
    r = anonimo.post("/login", data={"login": login, "senha": "x"})
    assert r.status_code in (401, 422)

def test_casas_decimais_por_campo(gestor):
    ok = lambda **kw: gestor.post("/produtos/", json={**BASE, **kw}).status_code
    assert ok(estoque_minimo="1.999") == 200   # quantidade: até 3 casas
    assert ok(preco_venda="1.99") == 200       # dinheiro: até 2 casas
    assert ok(preco_venda="1.999") == 422
    assert ok(preco_custo="1.999") == 422