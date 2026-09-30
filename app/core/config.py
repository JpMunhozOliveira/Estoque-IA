import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Sem valor padrão: quem conhece a chave consegue forjar sessões de qualquer usuário.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida")

HTTPS_ONLY = os.getenv("HTTPS_ONLY", "false").lower() == "true"

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/app/backups"))
BACKUP_TIMEOUT_SECONDS = int(os.getenv("BACKUP_TIMEOUT_SECONDS", "300"))
BACKUP_MAX_SIZE_MB = int(os.getenv("BACKUP_MAX_SIZE_MB", "50"))