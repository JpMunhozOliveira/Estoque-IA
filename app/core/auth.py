from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Usuario
from app.core.exceptions import RegraDeNegocioError, NaoAutenticadoError

OPERADOR_PODE = {("POST", "/movimentacoes/nova"), ("POST", "/movimentacoes/"), ("POST", "/usuarios/minha-senha")}

def usuario_atual(
        request: Request, 
        db: Session = Depends(get_db)
    ) -> Usuario:
    usuario_id = request.session.get("usuario_id")
    usuario = db.get(Usuario, usuario_id) if usuario_id else None
    if not usuario:
        request.session.clear()  # usuário removido ou sessão inválida
        raise NaoAutenticadoError()
    return usuario


def controle_de_acesso(
        request: Request, 
        usuario: Usuario = Depends(usuario_atual)
    ) -> Usuario:
    
    if usuario.papel == "gestor":
        return usuario

    caminho = request.url.path
    leitura = (request.method in ("GET", "HEAD", "OPTIONS") and not caminho.endswith(("/editar", "/redefinir-senha")))
    if leitura or (request.method, caminho) in OPERADOR_PODE:
        return usuario

    raise RegraDeNegocioError("Acesso negado: esta ação é permitida apenas para gestores.",status_code=403,
    )
