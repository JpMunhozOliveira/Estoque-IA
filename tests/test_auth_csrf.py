import re

def _token(c):
    return re.search(r'name="csrf_token" value="([^"]+)"', c.get("/usuarios/minha-senha").text).group(1)


def test_csrf_token_muda_a_cada_login(gestor):
    antes = gestor.csrf
    assert gestor.form("/logout").status_code == 303
    assert gestor.post("/login", data={"login": "gestor", "senha": "senha123"}).status_code == 303
    depois = _token(gestor)
    assert depois and depois != antes


def test_senha_limite_em_bytes(gestor):
    def novo(login, senha):
        return gestor.form("/usuarios/novo", nome="N", login=login, senha=senha, papel="operador").status_code
    assert novo("a", "ç" * 37) == 422        # 74 bytes
    assert novo("b", "ç" * 36) == 303        # 72 bytes exatos
    assert gestor.post("/usuarios/", json={"nome": "N", "login": "c", "senha": "ç" * 37}).status_code == 422

def test_login_errado_mensagem_igual_para_login_inexistente(anonimo, gestor):
    a = anonimo.post("/login", data={"login": "gestor", "senha": "errada"})
    b = anonimo.post("/login", data={"login": "naoexiste", "senha": "errada"})
    assert a.status_code == b.status_code == 401
    assert "inválidos" in a.text and "inválidos" in b.text


def test_logout(gestor):
    assert gestor.form("/logout").status_code == 303
    assert gestor.get("/produtos/pagina").status_code == 401


def test_csrf_token_muda_a_cada_login(gestor, anonimo):
    r = anonimo.post("/login", data={"login": "gestor", "senha": "senha123"})
    assert r.status_code == 303


def test_post_sem_csrf_ou_com_csrf_de_outro(gestor, operador):
    dados = {"nome": "X", "contato": ""}
    assert gestor.post("/clientes/novo", data=dados).status_code == 403
    assert gestor.post("/clientes/novo", data={**dados, "csrf_token": "errado"}).status_code == 403
    assert gestor.post("/clientes/novo", data={**dados, "csrf_token": operador.csrf}).status_code == 403
    assert gestor.form("/clientes/novo", **dados).status_code == 303


def test_alterar_minha_senha(operador, anonimo):
    ok = lambda s: anonimo.post("/login", data={"login": "operador", "senha": s}).status_code
    assert operador.form("/usuarios/minha-senha", senha_atual="errada",
                         nova_senha="novaSenha1", confirmar="novaSenha1").status_code == 400
    assert operador.form("/usuarios/minha-senha", senha_atual="senha123",
                         nova_senha="novaSenha1", confirmar="outra").status_code == 400
    assert operador.form("/usuarios/minha-senha", senha_atual="senha123",
                         nova_senha="123", confirmar="123").status_code == 422
    assert operador.form("/usuarios/minha-senha", senha_atual="senha123",
                         nova_senha="x" * 73, confirmar="x" * 73).status_code == 422
    assert operador.form("/usuarios/minha-senha", senha_atual="senha123",
                         nova_senha="novaSenha1", confirmar="novaSenha1").status_code == 303
    assert ok("senha123") == 401 and ok("novaSenha1") == 303


def test_gestor_cria_e_redefine_senha(gestor, anonimo):
    assert gestor.form("/usuarios/novo", nome="Ana", login="ana", senha="abcdef", papel="operador").status_code == 303
    assert gestor.form("/usuarios/novo", nome="Ana2", login="ana", senha="abcdef", papel="operador").status_code == 409
    assert gestor.form("/usuarios/novo", nome="B", login="b", senha="abcdef", papel="admin").status_code == 422
    assert gestor.form("/usuarios/novo", nome="C", login="   ", senha="abcdef", papel="operador").status_code == 422
    uid = [u["id"] for u in gestor.get("/usuarios/").json() if u["login"] == "ana"][0]
    assert gestor.form(f"/usuarios/{uid}/redefinir-senha", nova_senha="novasenha", confirmar="novasenha").status_code == 303
    assert anonimo.post("/login", data={"login": "ana", "senha": "novasenha"}).status_code == 303