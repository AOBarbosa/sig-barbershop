from fastapi import APIRouter, Depends

from app.dependencies import get_db
from app.schemas.historico_pontos_schema import HistoricoPontosResponse, SaldoPontosResponse
from app.services import historico_pontos_service

router = APIRouter(prefix="/clientes", tags=["historico-pontos"])


@router.get("/{cliente_id}/pontos", response_model=SaldoPontosResponse)
def buscar_saldo_pontos(cliente_id: int, conn=Depends(get_db)):
    return historico_pontos_service.buscar_saldo_pontos(conn, cliente_id)


@router.get("/{cliente_id}/pontos/historico", response_model=list[HistoricoPontosResponse])
def listar_historico_pontos(cliente_id: int, conn=Depends(get_db)):
    return historico_pontos_service.listar_historico_pontos(conn, cliente_id)
