import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import make_url

from app.core.config import (
    BACKUP_DIR,
    BACKUP_TIMEOUT_SECONDS,
    DATABASE_URL,
    BACKUP_MAX_SIZE_MB,
)
from app.core.exceptions import RegraDeNegocioError


def _garantir_pasta_backups() -> None:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _nome_valido(nome: str) -> bool:
    return bool(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.sql", nome)
    )

def obter_backup(nome: str) -> Path:
    if not _nome_valido(nome):
        raise RegraDeNegocioError("Nome de backup inválido.", status_code=400)

    arquivo = BACKUP_DIR / nome
    if not arquivo.is_file():
        raise RegraDeNegocioError("Backup não encontrado.", status_code=404)

    return arquivo


def listar_backups() -> list[dict]:
    _garantir_pasta_backups()

    arquivos = sorted(
        BACKUP_DIR.glob("*.sql"),
        key=lambda arquivo: arquivo.stat().st_mtime,
        reverse=True,
    )

    return [
        {
            "nome": arquivo.name,
            "tamanho": arquivo.stat().st_size,
            "criado_em": datetime.fromtimestamp(arquivo.stat().st_mtime),
        }
        for arquivo in arquivos
    ]


def criar_backup() -> Path:
    _garantir_pasta_backups()

    url = make_url(DATABASE_URL)
    nome = f"estoque_{datetime.now():%Y-%m-%d_%H-%M-%S_%f}.sql"
    destino = BACKUP_DIR / nome
    temporario = destino.with_suffix(".tmp")

    ambiente = os.environ.copy()
    if url.password:
        ambiente["PGPASSWORD"] = url.password

    comando = [
        "pg_dump",
        "--host", url.host or "db",
        "--port", str(url.port or 5432),
        "--username", url.username or "",
        "--format=plain",
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-privileges",
        "--file", str(temporario),
        url.database or "",
    ]

    try:
        subprocess.run(
            comando,
            env=ambiente,
            capture_output=True,
            text=True,
            check=True,
            timeout=BACKUP_TIMEOUT_SECONDS,
        )
        temporario.replace(destino)
        return destino
    except subprocess.TimeoutExpired:
        temporario.unlink(missing_ok=True)
        raise RegraDeNegocioError(
            "A geração do backup excedeu o tempo limite.",
            status_code=504,
        )
    except subprocess.CalledProcessError:
        temporario.unlink(missing_ok=True)
        raise RegraDeNegocioError(
            "Não foi possível gerar o backup do banco de dados.",
            status_code=500,
        )

def salvar_backup_enviado(nome_original: str, conteudo: bytes) -> Path:
    if not nome_original.lower().endswith(".sql"):
        raise RegraDeNegocioError(
            "Envie apenas arquivos com extensão .sql.",
            status_code=422,
        )

    limite_bytes = BACKUP_MAX_SIZE_MB * 1024 * 1024

    if not conteudo:
        raise RegraDeNegocioError(
            "O arquivo de backup está vazio.",
            status_code=422,
        )

    if len(conteudo) > limite_bytes:
        raise RegraDeNegocioError(
            f"O arquivo excede o limite de {BACKUP_MAX_SIZE_MB} MB.",
            status_code=413,
        )

    if b"\x00" in conteudo:
        raise RegraDeNegocioError(
            "O arquivo enviado não é um backup SQL válido.",
            status_code=422,
        )

    cabecalho = conteudo[:4096].decode("utf-8", errors="ignore")
    if "PostgreSQL database dump" not in cabecalho:
        raise RegraDeNegocioError(
            "Envie um backup SQL gerado pelo PostgreSQL.",
            status_code=422,
        )

    _garantir_pasta_backups()

    base = Path(nome_original).stem
    base_segura = re.sub(r"[^A-Za-z0-9_-]", "_", base)[:60] or "backup"

    nome = (
        f"enviado_{datetime.now():%Y-%m-%d_%H-%M-%S_%f}_"
        f"{base_segura}.sql"
    )
    destino = BACKUP_DIR / nome
    temporario = destino.with_suffix(".tmp")

    try:
        temporario.write_bytes(conteudo)
        temporario.replace(destino)
        return destino
    except OSError:
        temporario.unlink(missing_ok=True)
        raise RegraDeNegocioError(
            "Não foi possível salvar o arquivo de backup.",
            status_code=500,
        )

def restaurar_backup(nome: str) -> None:
    arquivo = obter_backup(nome)
    url = make_url(DATABASE_URL)

    ambiente = os.environ.copy()
    if url.password:
        ambiente["PGPASSWORD"] = url.password

    comando = [
        "psql",
        "--no-psqlrc",
        "--host", url.host or "db",
        "--port", str(url.port or 5432),
        "--username", url.username or "",
        "--dbname", url.database or "",
        "--set", "ON_ERROR_STOP=1",
        "--single-transaction",
        "--file", str(arquivo),
    ]

    try:
        subprocess.run(
            comando,
            env=ambiente,
            capture_output=True,
            text=True,
            check=True,
            timeout=BACKUP_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise RegraDeNegocioError(
            "A restauração excedeu o tempo limite.",
            status_code=504,
        )
    except subprocess.CalledProcessError:
        raise RegraDeNegocioError(
            "Não foi possível restaurar o backup selecionado.",
            status_code=500,
        )