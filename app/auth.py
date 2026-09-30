from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.exceptions import RegraDeNegocioError, NaoAutenticadoError

# Únicas escritas que o operador pode fazer
OPERADOR_PODE = {("POST", "/movimentacoes/nova"), ("POST", "/movimentacoes/")}


def usuario_atual(request: Request, db: Session = Depends(get_db)) -> Usuario:
    usuario_id = request.session.get("usuario_id")
    usuario = db.get(Usuario, usuario_id) if usuario_id else None
    if not usuario:
        request.session.clear()  # usuário removido ou sessão inválida
        raise NaoAutenticadoError()
    return usuario


def controle_de_acesso(request: Request, usuario: Usuario = Depends(usuario_atual)) -> Usuario:
    if usuario.papel == "gestor":
        return usuario

    caminho = request.url.path
    leitura = request.method in ("GET", "HEAD", "OPTIONS") and not caminho.endswith("/editar")
    if leitura or (request.method, caminho) in OPERADOR_PODE:
        return usuario

    raise RegraDeNegocioError("Acesso negado: esta ação é permitida apenas para gestores.", status_code=403)