from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.atendimento_schema import (
    AtendimentoCreate,
    AtendimentoResponse,
    AtendimentoServicoCreate,
    AtendimentoServicoResponse,
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


@router.get("/{atendimento_id}/servicos", response_model=list[AtendimentoServicoResponse])
def listar_servicos_atendimento(atendimento_id: int, conn=Depends(get_db)):
    return atendimento_service.listar_servicos_atendimento(conn, atendimento_id)


@router.post(
    "/{atendimento_id}/servicos",
    response_model=AtendimentoServicoResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_servico_atendimento(
    atendimento_id: int,
    payload: AtendimentoServicoCreate,
    conn=Depends(get_db),
):
    return atendimento_service.adicionar_servico_atendimento(conn, atendimento_id, payload)


@router.delete(
    "/{atendimento_id}/servicos/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_servico_atendimento(
    atendimento_id: int,
    servico_id: int,
    conn=Depends(get_db),
):
    atendimento_service.remover_servico_atendimento(conn, atendimento_id, servico_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
