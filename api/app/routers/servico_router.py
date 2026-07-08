from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db, require_funcionario
from app.schemas.servico_schema import (
    HistoricoServicoResponse,
    ServicoCreate,
    ServicoResponse,
    ServicoUpdate,
)
from app.services import servico_service

router = APIRouter(prefix="/servicos", tags=["servicos"])


@router.get("", response_model=list[ServicoResponse])
def listar_servicos(conn=Depends(get_db)):
    return servico_service.listar_servicos(conn)


@router.get("/{servico_id}", response_model=ServicoResponse)
def buscar_servico(servico_id: int, conn=Depends(get_db)):
    return servico_service.buscar_servico(conn, servico_id)


@router.get("/{servico_id}/historico", response_model=list[HistoricoServicoResponse])
def listar_historico_servico(servico_id: int, conn=Depends(get_db)):
    return servico_service.listar_historico_servico(conn, servico_id)


@router.post(
    "",
    response_model=ServicoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_funcionario)],
)
def criar_servico(payload: ServicoCreate, conn=Depends(get_db)):
    return servico_service.criar_servico(conn, payload)


@router.put(
    "/{servico_id}", response_model=ServicoResponse, dependencies=[Depends(require_funcionario)]
)
def atualizar_servico(servico_id: int, payload: ServicoUpdate, conn=Depends(get_db)):
    return servico_service.atualizar_servico(conn, servico_id, payload)


@router.delete(
    "/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_funcionario)],
)
def deletar_servico(servico_id: int, conn=Depends(get_db)):
    servico_service.deletar_servico(conn, servico_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
