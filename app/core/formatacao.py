import re
from decimal import Decimal

from app.core.exceptions import RegraDeNegocioError

_PADRAO = re.compile(r"\d{1,3}(\.\d{3})+(,\d{1,2})?|\d+(,\d{1,2})?")


def _numero_br(valor) -> str:
    v = Decimal(valor or 0).quantize(Decimal("0.01"))
    inteiro, _, centavos = f"{v:,.2f}".partition(".")
    return f"{inteiro.replace(',', '.')},{centavos}"


def reais_input(valor) -> str:
    """1234.5 -> '1.234,50' (para o value do input)."""
    return _numero_br(valor)


def brl(valor) -> str:
    """1234.5 -> 'R$ 1.234,50' (para exibição)."""
    return "-" if valor is None else f"R$ {_numero_br(valor)}"


def parse_reais(texto: str, campo: str = "valor") -> Decimal:
    """'1.234,50' -> Decimal('1234.50'). Vazio vira 0."""
    t = (texto or "").replace("R$", "").replace("\xa0", "").strip()
    if not t:
        return Decimal("0")
    if not _PADRAO.fullmatch(t):
        raise RegraDeNegocioError(f"{campo}: valor inválido. Use o formato 1.234,50", status_code=422)
    return Decimal(t.replace(".", "").replace(",", "."))