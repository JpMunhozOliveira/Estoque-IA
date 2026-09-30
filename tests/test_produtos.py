from decimal import Decimal

D = lambda v: Decimal(str(v))  # o JSON devolve Decimal como string

BASE = {"nome": "Parafuso", "categoria": "Fixação", "unidade": "cx",
        "estoque_minimo": "5", "preco_custo": "1.50", "preco_venda": "3.00"}


def test_crud_completo_api(gestor, make_fornecedor):
    f = make_fornecedor()
    r = gestor.post("/produtos/", json={**BASE, "fornecedor_id": f.id})
    assert r.status_code == 200
    p = r.json()
    assert D(p["quantidade"]) == 0          # começa zerado
    pid = p["id"]

    assert len(gestor.get("/produtos/", params={"nome": "parafu"}).json()) == 1
    assert gestor.get("/produtos/", params={"nome": "xxx"}).json() == []

    r = gestor.put(f"/produtos/{pid}", json={**BASE, "nome": "Parafuso M8", "preco_venda": "4.25"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Parafuso M8" and D(r.json()["preco_venda"]) == D("4.25")

    assert gestor.delete(f"/produtos/{pid}").status_code == 200
    assert gestor.get("/produtos/").json() == []


def test_quantidade_nao_pode_ser_enviada(gestor, make_produto):
    assert gestor.post("/produtos/", json={**BASE, "quantidade": 50}).status_code == 422
    p = make_produto()
    assert gestor.put(f"/produtos/{p.id}", json={**BASE, "quantidade": 50}).status_code == 422


def test_fornecedor_inexistente(gestor):
    assert gestor.post("/produtos/", json={**BASE, "fornecedor_id": 9999}).status_code == 404


def test_filtros(gestor, make_produto, make_fornecedor):
    f = make_fornecedor()
    make_produto(nome="Barato", categoria="A", preco_venda=Decimal("1"))
    make_produto(nome="Caro", categoria="B", preco_venda=Decimal("100"), fornecedor_id=f.id)
    nomes = lambda **q: [p["nome"] for p in gestor.get("/produtos/", params=q).json()]
    assert nomes(categoria="b") == ["Caro"]
    assert nomes(preco_min=50) == ["Caro"]
    assert nomes(preco_max=50) == ["Barato"]
    assert nomes(fornecedor_id=f.id) == ["Caro"]


def test_abaixo_do_minimo(gestor, make_produto):
    make_produto(nome="Baixo", estoque_minimo=Decimal("10"))   # qtd 0 < 10
    make_produto(nome="SemMinimo", estoque_minimo=Decimal("0"))
    assert [p["nome"] for p in gestor.get("/produtos/", params={"abaixo_minimo": True}).json()] == ["Baixo"]


# ---- Web (formulário + CSRF) ----
def test_web_criar_editar_remover(gestor):
    r = gestor.form("/produtos/novo", nome="Web", categoria="", unidade="un",
                    estoque_minimo="1", preco_custo="1", preco_venda="2", fornecedor_id="")
    assert r.status_code == 303
    pid = gestor.get("/produtos/").json()[0]["id"]
    r = gestor.form(f"/produtos/{pid}/editar", nome="Web2", categoria="", unidade="un",
                    estoque_minimo="1", preco_custo="1", preco_venda="2", fornecedor_id="")
    assert r.status_code == 303
    assert gestor.get("/produtos/").json()[0]["nome"] == "Web2"
    assert gestor.form(f"/produtos/{pid}/remover").status_code == 303
    assert gestor.get("/produtos/").json() == []