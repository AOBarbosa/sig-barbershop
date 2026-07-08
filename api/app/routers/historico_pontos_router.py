from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, get_db
from app.schemas.historico_pontos_schema import HistoricoPontosResponse, SaldoPontosResponse
from app.services import historico_pontos_service

router = APIRouter(prefix="/clientes", tags=["historico-pontos"])


def _validar_acesso(usuario: dict, cliente_id: int) -> None:
    if usuario["role"] in ("admin", "funcionario"):
        return
    if usuario["role"] == "cliente" and usuario["id_pessoa"] == cliente_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso restrito ao proprio cliente ou a funcionarios",
    )


@router.get("/{cliente_id}/pontos", response_model=SaldoPontosResponse)
def buscar_saldo_pontos(
    cliente_id: int, usuario=Depends(get_current_user), conn=Depends(get_db)
):
    _validar_acesso(usuario, cliente_id)
    return historico_pontos_service.buscar_saldo_pontos(conn, cliente_id)


@router.get("/{cliente_id}/pontos/historico", response_model=list[HistoricoPontosResponse])
def listar_historico_pontos(
    cliente_id: int, usuario=Depends(get_current_user), conn=Depends(get_db)
):
    _validar_acesso(usuario, cliente_id)
    return historico_pontos_service.listar_historico_pontos(conn, cliente_id)
