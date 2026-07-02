from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.atendimento_schema import (
    AtendimentoCreate,
    AtendimentoResponse,
    AtendimentoStatusUpdate,
    AtendimentoUpdate,
)
from app.services import atendimento_service

router = APIRouter(prefix="/atendimentos", tags=["atendimentos"])


@router.get("", response_model=list[AtendimentoResponse])
def listar_atendimentos(conn=Depends(get_db)):
    return atendimento_service.listar_atendimentos(conn)


@router.get("/{atendimento_id}", response_model=AtendimentoResponse)
def buscar_atendimento(atendimento_id: int, conn=Depends(get_db)):
    return atendimento_service.buscar_atendimento(conn, atendimento_id)


@router.post("", response_model=AtendimentoResponse, status_code=status.HTTP_201_CREATED)
def criar_atendimento(payload: AtendimentoCreate, conn=Depends(get_db)):
    return atendimento_service.criar_atendimento(conn, payload)


@router.put("/{atendimento_id}", response_model=AtendimentoResponse)
def atualizar_atendimento(
    atendimento_id: int,
    payload: AtendimentoUpdate,
    conn=Depends(get_db),
):
    return atendimento_service.atualizar_atendimento(conn, atendimento_id, payload)


@router.patch("/{atendimento_id}/status", response_model=AtendimentoResponse)
def atualizar_status_atendimento(
    atendimento_id: int,
    payload: AtendimentoStatusUpdate,
    conn=Depends(get_db),
):
    return atendimento_service.atualizar_status_atendimento(conn, atendimento_id, payload)


@router.delete("/{atendimento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_atendimento(atendimento_id: int, conn=Depends(get_db)):
    atendimento_service.deletar_atendimento(conn, atendimento_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
