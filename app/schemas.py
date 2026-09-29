from decimal import Decimal
from typing import Annotated, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Tipos reutilizáveis: a regra fica definida uma vez só e vale em todos os campos
Dinheiro = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Quantidade = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=3)]
QuantidadeMovimentada = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=3)]
TipoMovimentacao = Literal["entrada", "saida"]


class ProdutoBase(BaseModel):
    nome: str
    categoria: Optional[str] = None
    unidade: str = "unidade"
    estoque_minimo: Quantidade = Decimal("0")
    preco_custo: Dinheiro = Decimal("0")
    preco_venda: Dinheiro = Decimal("0")
    fornecedor_id: Optional[int] = None

class ProdutoCreate(ProdutoBase):
    # "quantidade" não é campo de entrada: o estoque só muda por Movimentação.
    # Com extra="forbid", enviar "quantidade" gera erro em vez de ser ignorado.
    model_config = ConfigDict(extra="forbid")

class ProdutoResponse(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade: Decimal
    criado_em: datetime

class FornecedorBase(BaseModel):
    nome: str
    contato: Optional[str] = None

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorResponse(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ClienteBase(BaseModel):
    nome: str
    contato: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class UsuarioBase(BaseModel):
    nome: str
    login: str
    papel: str = "operador"

class UsuarioCreate(UsuarioBase):
    senha: str  # senha em texto puro, só na entrada — nunca fica salva assim

class UsuarioResponse(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class MovimentacaoBase(BaseModel):
    produto_id: int
    usuario_id: int
    cliente_id: Optional[int] = None
    tipo: TipoMovimentacao
    quantidade: QuantidadeMovimentada
    valor_unitario: Dinheiro = Decimal("0")

class MovimentacaoCreate(MovimentacaoBase):
    pass

class MovimentacaoResponse(MovimentacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data: datetime
