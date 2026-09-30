from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.services import backup as backup_service
from app.core.exceptions import RegraDeNegocioError
from app.core.config import BACKUP_MAX_SIZE_MB
from app.db.database import get_db

router = APIRouter(prefix="/backups", tags=["Backups - Web"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/pagina")
def pagina_backups(request: Request):
    return templates.TemplateResponse(
        request,
        "backups/index.html",
        {"backups": backup_service.listar_backups()},
    )

@router.post("/gerar")
def gerar_backup():
    arquivo = backup_service.criar_backup()

    return FileResponse(
        path=arquivo,
        media_type="application/sql",
        filename=arquivo.name,
        headers={"Cache-Control": "no-store"},
    )

@router.post("/enviar")
async def enviar_backup(arquivo: UploadFile = File(...)):
    limite_bytes = BACKUP_MAX_SIZE_MB * 1024 * 1024
    conteudo = bytearray()

    try:
        while bloco := await arquivo.read(1024 * 1024):
            if len(conteudo) + len(bloco) > limite_bytes:
                raise RegraDeNegocioError(
                    f"O arquivo excede o limite de {BACKUP_MAX_SIZE_MB} MB.",
                    status_code=413,
                )
            conteudo.extend(bloco)

        backup_service.salvar_backup_enviado(
            arquivo.filename or "",
            bytes(conteudo),
        )
    finally:
        await arquivo.close()

    return RedirectResponse(url="/backups/pagina", status_code=303)

@router.get("/{nome}/download")
def baixar_backup(nome: str):
    arquivo = backup_service.obter_backup(nome)

    return FileResponse(
        path=arquivo,
        media_type="application/sql",
        filename=arquivo.name,
        headers={"Cache-Control": "no-store"},
    )

@router.post("/restaurar")
def restaurar_backup(
    request: Request,
    nome: str = Form(...),
    confirmar_nome: str = Form(...),
    db: Session = Depends(get_db),
):
    if nome != confirmar_nome:
        raise RegraDeNegocioError(
            "A confirmação deve ser exatamente igual ao nome do backup.",
            status_code=400,
        )

    # Libera a conexão usada pela autenticação antes de o psql substituir as tabelas.
    db.close()

    backup_service.restaurar_backup(nome)

    # A base restaurada pode ter usuários, senhas e IDs diferentes.
    request.session.clear()

    return RedirectResponse(url="/login", status_code=303)