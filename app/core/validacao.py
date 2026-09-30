from fastapi import Request

from app.core.exceptions import RegraDeNegocioError

_MSG = "Requisição inválida: o caractere nulo (\\x00) não é permitido."


def _tem_nul(texto) -> bool:
    return isinstance(texto, str) and "\x00" in texto


async def rejeitar_nul(request: Request):
    """O PostgreSQL não aceita NUL em texto; sem isso o psycopg2 estoura e vira 500."""
    if any(_tem_nul(k) or _tem_nul(v) for k, v in request.query_params.multi_items()):
        raise RegraDeNegocioError(_MSG, status_code=422)

    tipo = request.headers.get("content-type", "")
    if tipo.startswith(("application/x-www-form-urlencoded", "multipart/form-data")):
        form = await request.form()
        if any(_tem_nul(k) or _tem_nul(v) for k, v in form.multi_items()):
            raise RegraDeNegocioError(_MSG, status_code=422)
    elif tipo.startswith("application/json"):
        corpo = await request.body()
        # JSON escapa NUL como \u0000; o byte cru também é recusado
        if b"\\u0000" in corpo or b"\x00" in corpo:
            raise RegraDeNegocioError(_MSG, status_code=422)