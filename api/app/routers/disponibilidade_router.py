from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db, require_funcionario
from app.schemas.disponibilidade_schema import (
    DisponibilidadeCreate,
    DisponibilidadeResponse,
    DisponibilidadeUpdate,
)
from app.services import disponibilidade_service

router = APIRouter(prefix="/disponibilidades", tags=["disponibilidades"])


@router.get("/{disponibilidade_id}", response_model=DisponibilidadeResponse)
def buscar_disponibilidade(disponibilidade_id: int, conn=Depends(get_db)):
    return disponibilidade_service.buscar_disponibilidade(conn, disponibilidade_id)


@router.post(
    "",
    response_model=DisponibilidadeResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_funcionario)],
)
def criar_disponibilidade(payload: DisponibilidadeCreate, conn=Depends(get_db)):
    return disponibilidade_service.criar_disponibilidade(conn, payload)


@router.put(
    "/{disponibilidade_id}",
    response_model=DisponibilidadeResponse,
    dependencies=[Depends(require_funcionario)],
)
def atualizar_disponibilidade(
    disponibilidade_id: int,
    payload: DisponibilidadeUpdate,
    conn=Depends(get_db),
):
    return disponibilidade_service.atualizar_disponibilidade(conn, disponibilidade_id, payload)


@router.delete(
    "/{disponibilidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_funcionario)],
)
def deletar_disponibilidade(disponibilidade_id: int, conn=Depends(get_db)):
    disponibilidade_service.deletar_disponibilidade(conn, disponibilidade_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
