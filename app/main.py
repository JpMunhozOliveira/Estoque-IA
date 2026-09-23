from fastapi import FastAPI
from database import engine

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "funcionando"}

@app.get("/test-db")
def test_db():
    try:
        conn = engine.connect()
        conn.close()
        return {"banco": "conectado com sucesso"}
    except Exception as e:
        return {"erro": str(e)}