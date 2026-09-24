from fastapi import FastAPI
from app.database import engine, Base
from app.models import Produto, Fornecedor, Cliente, Usuario, Movimentacao
from app.routes_produto import router as produto_router
from app.routes_fornecedor import router as fornecedor_router
from app.routes_cliente import router as cliente_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(produto_router)
app.include_router(fornecedor_router)
app.include_router(cliente_router)

@app.get("/")
def read_root():
    return {"status": "funcionando"}
