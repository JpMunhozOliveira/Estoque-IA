from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Optional
from app.db.database import get_db
from app.schemas.schemas import MovimentacaoCreate, MovimentacaoResponse
from app.services import movimentacao as movimentacao_service
from app.core.auth import usuario_atual
from app.models.models import Usuario

router = APIRouter(prefix="/movimentacoes", tags=["Movimentações"])

@router.post("/", response_model=MovimentacaoResponse)
def criar_movimentacao(
    mov: MovimentacaoCreate, 
    db: Session = Depends(get_db), 
    usuario: Usuario = Depends(usuario_atual)
):
    return movimentacao_service.criar_movimentacao(db, mov.model_dump(), usuario.id)

@router.get("/", response_model=list[MovimentacaoResponse])
def listar_movimentacoes(
    produto_id: Optional[int] = None, 
    tipo: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return movimentacao_service.listar_movimentacoes(db, produto_id, tipo)