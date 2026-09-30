from pydantic import ValidationError

class RegraDeNegocioError(Exception):
    """Erro de regra de negócio (dado inválido, exclusão bloqueada, etc.).
    Os services levantam este erro; o main.py transforma em resposta HTTP.
    Assim os services não dependem do FastAPI e podem ser reaproveitados
    (por exemplo, pelas funções que o agente de IA vai chamar).
    """

    def __init__(self, mensagem: str, status_code: int = 400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


def validar(schema, dados: dict):
    """Valida um dict com um schema Pydantic e devolve o objeto validado.
    Se algo estiver errado, converte o erro do Pydantic em RegraDeNegocioError.
    """
    try:
        return schema.model_validate(dados)
    except ValidationError as erro:
        detalhes = "; ".join(
            f"{'.'.join(str(parte) for parte in e['loc'])}: {e['msg']}"
            for e in erro.errors()
        )
        raise RegraDeNegocioError(detalhes, status_code=422)

class NaoAutenticadoError(Exception):
    """Usuário sem sessão válida."""