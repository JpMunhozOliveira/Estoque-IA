from decimal import Decimal
from typing import Annotated, Literal, Optional
from datetime import datetime
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoOpcional = Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]]
Dinheiro = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Quantidade = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=3)]
QuantidadeMovimentada = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=3)]
TipoMovimentacao = Literal["entrada", "saida"]

# Produtos

class ProdutoBase(BaseModel):
    nome: Nome
    categoria: TextoOpcional = None
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

# Fornecedores

class FornecedorBase(BaseModel):
    nome: Nome
    contato: TextoOpcional = None

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorResponse(FornecedorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# Clientes

class ClienteBase(BaseModel):
    nome: Nome
    contato: TextoOpcional = None

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

# Usuários

Papel = Literal["operador", "gestor"]
def _senha_cabe_no_bcrypt(senha: str) -> str:
    if len(senha.encode("utf-8")) > 72:
        raise ValueError("a senha deve ter no máximo 72 bytes (acentos contam mais de 1)")
    return senha

Senha = Annotated[str, Field(min_length=6, max_length=72), AfterValidator(_senha_cabe_no_bcrypt)]

class UsuarioBase(BaseModel):
    nome: str = Field(min_length=1)
    login: str = Field(min_length=1)
    papel: Papel = "operador"

class UsuarioCreate(UsuarioBase):
    senha: Senha

class SenhaNova(BaseModel):
    senha: Senha

class UsuarioResponse(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Movimentações

class MovimentacaoBase(BaseModel):
    produto_id: int
    cliente_id: Optional[int] = None
    tipo: TipoMovimentacao
    quantidade: QuantidadeMovimentada
    valor_unitario: Dinheiro = Decimal("0")

class MovimentacaoCreate(MovimentacaoBase):
    pass

class MovimentacaoResponse(MovimentacaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    data: datetime
