import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Sem valor padrão: quem conhece a chave consegue forjar sessões de qualquer usuário
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida")

HTTPS_ONLY = os.getenv("HTTPS_ONLY", "false").lower() == "true"