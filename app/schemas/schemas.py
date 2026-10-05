from decimal import Decimal
from typing import Annotated, Literal, Optional
from datetime import datetime
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints, model_validator

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoOpcional = Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=200)]]

# Produtos
Dinheiro = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Quantidade = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=3)]

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

TipoMovimentacao = Literal["entrada", "saida", "ajuste"]
MotivoAjuste = Literal["avaria", "perda", "contagem", "erro_lancamento", "divergencia", "outro"]
# Com sinal: no ajuste é a diferença (+/-); entrada/saída exigem > 0 no validador abaixo
QuantidadeComSinal = Annotated[Decimal, Field(max_digits=12, decimal_places=3)]
QuantidadeMovimentada = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=3)]

class MovimentacaoBase(BaseModel):
    produto_id: int
    cliente_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    tipo: TipoMovimentacao
    quantidade: QuantidadeComSinal
    valor_unitario: Dinheiro = Decimal("0")
    documento: Optional[str] = Field(default=None, max_length=60)
    observacao: Optional[str] = Field(default=None, max_length=500)
    motivo_ajuste: Optional[MotivoAjuste] = None

class MovimentacaoCreate(MovimentacaoBase):
    @model_validator(mode="after")
    def _regras_por_tipo(self):
        if self.tipo == "entrada":
            if self.cliente_id is not None:
                raise ValueError("entrada não pode ter cliente (use fornecedor)")
        elif self.tipo == "saida":
            if self.fornecedor_id is not None:
                raise ValueError("saída não pode ter fornecedor (use cliente)")
        else:  # ajuste
            if self.fornecedor_id is not None or self.cliente_id is not None:
                raise ValueError("ajuste não tem fornecedor nem cliente")
            if self.motivo_ajuste is None:
                raise ValueError("ajuste exige um motivo")
            if self.quantidade == 0:
                raise ValueError("ajuste com diferença zero não faz sentido")
            return self

        if self.quantidade <= 0:
            raise ValueError("quantidade deve ser maior que zero")
        if self.motivo_ajuste is not None:
            raise ValueError("motivo_ajuste só vale para ajuste")
        return self

class MovimentacaoResponse(MovimentacaoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    usuario_id: int
    data: datetime
