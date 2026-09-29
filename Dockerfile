FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia o projeto inteiro (app/, alembic/, alembic.ini) para a imagem ficar autossuficiente
COPY . .

# Aplica as migrations e só depois sobe a API
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]