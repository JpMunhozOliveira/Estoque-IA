from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProdutoBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    quantidade: float = 0
    unidade: str = "unidade"
    estoque_minimo: float = 0
    preco_custo: float = 0
    preco_venda: float = 0
    fornecedor_id: Optional[int] = None

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoResponse(ProdutoBase):
    id: int
    criado_em: datetime

    class Config:
        from_attributes = True

class FornecedorBase(BaseModel):
    nome: str
    contato: Optional[str] = None

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorResponse(FornecedorBase):
    id: int

    class Config:
        from_attributes = True


class ClienteBase(BaseModel):
    nome: str
    contato: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int

    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nome: str
    login: str
    papel: str = "operador"

class UsuarioCreate(UsuarioBase):
    senha: str  # senha em texto puro, só na entrada — nunca fica salva assim

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True

class MovimentacaoBase(BaseModel):
    produto_id: int
    usuario_id: int
    cliente_id: Optional[int] = None
    tipo: str  # "entrada" ou "saida"
    quantidade: float
    valor_unitario: float = 0

class MovimentacaoCreate(MovimentacaoBase):
    pass

class MovimentacaoResponse(MovimentacaoBase):
    id: int
    data: datetime

    class Config:
        from_attributes = True