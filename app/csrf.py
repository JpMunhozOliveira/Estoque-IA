import secrets
from fastapi import Request
from app.exceptions import RegraDeNegocioError

_TIPOS_FORM = ("application/x-www-form-urlencoded", "multipart/form-data")


async def verificar_csrf(request: Request):
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    if not request.headers.get("content-type", "").startswith(_TIPOS_FORM):
        return  # JSON: o navegador exige preflight CORS, que não está habilitado

    form = await request.form()
    enviado = str(form.get("csrf_token", "")).encode()
    esperado = str(request.session.get("csrf_token", "")).encode()
    if not esperado or not secrets.compare_digest(enviado, esperado):
        raise RegraDeNegocioError(
            "Requisição inválida (token CSRF). Recarregue a página ou entre de novo.",
            status_code=403,
        )