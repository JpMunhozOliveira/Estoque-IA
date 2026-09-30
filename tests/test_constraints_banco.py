import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


@pytest.mark.parametrize("coluna", ["quantidade", "estoque_minimo", "preco_custo", "preco_venda"])
def test_produto_nao_aceita_negativo(db, coluna):
    with pytest.raises(IntegrityError):
        db.execute(text(f"INSERT INTO produtos (nome, {coluna}) VALUES ('x', -1)"))
    db.rollback()


def _inserir_mov(db, produto_id, usuario_id, tipo="entrada", qtd=1, valor=0):
    db.execute(text(
        "INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, valor_unitario) "
        "VALUES (:p, :u, :t, :q, :v)"),
        {"p": produto_id, "u": usuario_id, "t": tipo, "q": qtd, "v": valor})


def test_movimentacao_valida_entra(db, gestor, make_produto):
    _inserir_mov(db, make_produto().id, gestor.usuario_id)   # controle: sem isso os outros podem falhar por outro motivo
    db.commit()


@pytest.mark.parametrize("tipo,qtd,valor", [
    ("transferencia", 1, 0),
    ("entrada", 0, 0),
    ("entrada", -1, 0),
    ("entrada", 1, -1),
])
def test_movimentacao_invalida_barrada(db, gestor, make_produto, tipo, qtd, valor):
    pid = make_produto().id
    with pytest.raises(IntegrityError):
        _inserir_mov(db, pid, gestor.usuario_id, tipo, qtd, valor)
    db.rollback()


def test_fk_e_unique(db, gestor, make_produto):
    with pytest.raises(IntegrityError):                       # produto inexistente
        _inserir_mov(db, 99999, gestor.usuario_id)
    db.rollback()
    with pytest.raises(IntegrityError):                       # login duplicado
        db.execute(text("INSERT INTO usuarios (nome, login, senha_hash) VALUES ('x', 'gestor', 'h')"))
    db.rollback()