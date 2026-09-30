FROM python:3.12-slim

WORKDIR /app

# Ferramentas PostgreSQL 16 usadas para gerar e restaurar backups.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && install -d -m 0755 /usr/share/postgresql-common/pgdg \
    && curl --fail --silent --show-error \
        -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && . /etc/os-release \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia o projeto inteiro (app/, alembic/, alembic.ini) para a imagem ficar autossuficiente
COPY . .

# Aplica as migrations e só depois sobe a API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]