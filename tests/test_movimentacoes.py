from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest


def mov(c, pid, tipo, qtd, **extra):
    return c.post("/movimentacoes/", json={"produto_id": pid, "tipo": tipo, "quantidade": str(qtd), **extra})


def test_entrada_e_saida(gestor, make_produto, estoque):
    pid = make_produto().id
    assert mov(gestor, pid, "entrada", "10.5").status_code == 200
    assert mov(gestor, pid, "saida", "4.25").status_code == 200
    assert estoque(pid) == Decimal("6.250")


def test_saida_maior_que_estoque(gestor, make_produto, estoque):
    pid = make_produto().id
    mov(gestor, pid, "entrada", 5)
    r = mov(gestor, pid, "saida", "5.001")
    assert r.status_code == 400
    assert estoque(pid) == 5                       # nada mudou
    assert mov(gestor, pid, "saida", 5).status_code == 200   # exatamente o que tem
    assert estoque(pid) == 0


@pytest.mark.parametrize("qtd", ["0", "-1", "abc", "", "0.0001", "1e20", "NaN", "Infinity"])
def test_quantidade_invalida(gestor, make_produto, estoque, qtd):
    pid = make_produto().id
    assert mov(gestor, pid, "entrada", qtd).status_code == 422
    assert estoque(pid) == 0


def test_tipo_invalido_e_inexistentes(gestor, make_produto):
    pid = make_produto().id
    assert mov(gestor, pid, "transferencia", 1).status_code == 422
    assert mov(gestor, 99999, "entrada", 1).status_code == 404
    assert mov(gestor, pid, "entrada", 1, cliente_id=99999).status_code == 404


def test_usuario_vem_da_sessao_e_nao_do_corpo(gestor, operador, make_produto):
    pid = make_produto().id
    r = mov(operador, pid, "entrada", 1, usuario_id=gestor.usuario_id)   # tentativa de forjar
    assert r.status_code == 200
    assert r.json()["usuario_id"] == operador.usuario_id


def test_filtros_listagem(gestor, make_produto):
    a, b = make_produto(nome="A").id, make_produto(nome="B").id
    mov(gestor, a, "entrada", 5); mov(gestor, a, "saida", 1); mov(gestor, b, "entrada", 2)
    assert len(gestor.get("/movimentacoes/", params={"produto_id": a}).json()) == 2
    assert len(gestor.get("/movimentacoes/", params={"tipo": "saida"}).json()) == 1


def test_operador_registra_movimentacao_pela_web(operador, make_produto, estoque):
    pid = make_produto().id
    r = operador.form("/movimentacoes/nova", produto_id=pid, cliente_id="", tipo="entrada",
                      quantidade="3", valor_unitario="0")
    assert r.status_code == 303 and estoque(pid) == 3


def test_duas_saidas_simultaneas_nao_estouram_estoque(gestor, operador, make_produto, estoque):
    pid = make_produto().id
    mov(gestor, pid, "entrada", 10)
    with ThreadPoolExecutor(2) as ex:
        codigos = list(ex.map(lambda c: mov(c, pid, "saida", 10).status_code, [gestor, operador]))
    assert sorted(codigos) == [200, 400]     # with_for_update funcionando
    assert estoque(pid) == 0


# ---- Exclusões bloqueadas por vínculo ----
def test_nao_remove_com_vinculos(gestor, operador, make_produto, make_cliente, make_fornecedor):
    f = make_fornecedor()
    p = make_produto(fornecedor_id=f.id)
    c = make_cliente()
    mov(gestor, p.id, "entrada", 5, cliente_id=c.id)
    assert gestor.delete(f"/fornecedores/{f.id}").status_code == 409   # tem produto
    assert gestor.delete(f"/produtos/{p.id}").status_code == 409       # tem movimentação
    assert gestor.delete(f"/clientes/{c.id}").status_code == 409       # tem movimentação
    mov(operador, p.id, "entrada", 1)
    assert gestor.delete(f"/usuarios/{operador.usuario_id}").status_code == 409
    