import pytest

@pytest.mark.parametrize("caminho", ["/docs", "/redoc", "/openapi.json"])
def test_docs_desligadas_por_padrao(anonimo, caminho):
    assert anonimo.get(caminho).status_code == 404