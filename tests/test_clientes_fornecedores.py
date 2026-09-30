import pytest

ENTIDADES = ["clientes", "fornecedores"]


@pytest.mark.parametrize("base", ENTIDADES)
def test_crud_api(gestor, base):
    r = gestor.post(f"/{base}/", json={"nome": "  Acme  ", "contato": "11 9999"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Acme"                      # strip aplicado
    eid = r.json()["id"]

    assert len(gestor.get(f"/{base}/", params={"nome": "acm"}).json()) == 1
    assert gestor.get(f"/{base}/", params={"nome": "xxx"}).json() == []

    r = gestor.put(f"/{base}/{eid}", json={"nome": "Acme 2"})
    assert r.status_code == 200 and r.json()["nome"] == "Acme 2"
    assert gestor.get(f"/{base}/{eid}").json()["nome"] == "Acme 2"

    assert gestor.delete(f"/{base}/{eid}").status_code == 200
    assert gestor.get(f"/{base}/{eid}").status_code == 404


@pytest.mark.parametrize("base", ENTIDADES)
def test_crud_web(gestor, base):
    assert gestor.form(f"/{base}/novo", nome="Acme", contato="11 9999").status_code == 303
    itens = gestor.get(f"/{base}/").json()
    assert [i["nome"] for i in itens] == ["Acme"]
    eid = itens[0]["id"]

    assert "Acme" in gestor.get(f"/{base}/pagina").text
    assert "Acme" in gestor.get(f"/{base}/{eid}/editar").text

    assert gestor.form(f"/{base}/{eid}/editar", nome="Acme 2", contato="").status_code == 303
    assert gestor.get(f"/{base}/{eid}").json()["nome"] == "Acme 2"

    assert gestor.form(f"/{base}/{eid}/remover").status_code == 303
    assert gestor.get(f"/{base}/").json() == []


@pytest.mark.parametrize("base", ENTIDADES)
@pytest.mark.parametrize("nome", ["", "   ", "x" * 201])
def test_nome_invalido(gestor, base, nome):
    assert gestor.post(f"/{base}/", json={"nome": nome}).status_code == 422
    assert gestor.form(f"/{base}/novo", nome=nome, contato="").status_code == 422
    assert gestor.get(f"/{base}/").json() == []            # nada foi gravado


@pytest.mark.parametrize("base", ENTIDADES)
def test_editar_com_nome_invalido_nao_altera(gestor, base):
    eid = gestor.post(f"/{base}/", json={"nome": "Original"}).json()["id"]
    assert gestor.form(f"/{base}/{eid}/editar", nome="  ", contato="").status_code == 422
    assert gestor.put(f"/{base}/{eid}", json={"nome": ""}).status_code == 422
    assert gestor.get(f"/{base}/{eid}").json()["nome"] == "Original"


@pytest.mark.parametrize("base", ENTIDADES)
def test_inexistente_nas_rotas_web(gestor, base):
    assert gestor.get(f"/{base}/999/editar").status_code == 404
    assert gestor.form(f"/{base}/999/editar", nome="X", contato="").status_code == 404
    assert gestor.form(f"/{base}/999/remover").status_code == 404


def test_remover_fornecedor_com_produto_pela_web(gestor, make_fornecedor, make_produto):
    f = make_fornecedor()
    make_produto(fornecedor_id=f.id)
    assert gestor.form(f"/fornecedores/{f.id}/remover").status_code == 409
    assert len(gestor.get("/fornecedores/").json()) == 1


def test_remover_cliente_com_movimentacao_pela_web(gestor, make_cliente, make_produto):
    c, p = make_cliente(), make_produto()
    gestor.post("/movimentacoes/", json={"produto_id": p.id, "tipo": "entrada",
                                         "quantidade": "1", "cliente_id": c.id})
    assert gestor.form(f"/clientes/{c.id}/remover").status_code == 409