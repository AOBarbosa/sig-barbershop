from datetime import datetime

from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user_opcional, get_db, require_admin
from app.schemas.barbeiro_schema import (
    BarbeiroCompletoCreate,
    BarbeiroCompletoResponse,
    BarbeiroCompletoUpdate,
    BarbeiroCreate,
    BarbeiroResponse,
    BarbeiroUpdate,
)
from app.schemas.disponibilidade_schema import DisponibilidadeResponse
from app.services import agenda_service, barbeiro_service, disponibilidade_service

router = APIRouter(prefix="/barbeiros", tags=["barbeiros"])


def _ocultar_comissao(barbeiro: dict, usuario: dict | None) -> dict:
    if usuario and usuario["role"] == "admin":
        return barbeiro
    return barbeiro | {"comissao_percentual": None}


@router.get("", response_model=list[BarbeiroResponse])
def listar_barbeiros(usuario=Depends(get_current_user_opcional), conn=Depends(get_db)):
    barbeiros = barbeiro_service.listar_barbeiros(conn)
    return [_ocultar_comissao(b, usuario) for b in barbeiros]


@router.get("/{barbeiro_id}", response_model=BarbeiroResponse)
def buscar_barbeiro(
    barbeiro_id: int, usuario=Depends(get_current_user_opcional), conn=Depends(get_db)
):
    barbeiro = barbeiro_service.buscar_barbeiro(conn, barbeiro_id)
    return _ocultar_comissao(barbeiro, usuario)


@router.get("/{barbeiro_id}/disponibilidades", response_model=list[DisponibilidadeResponse])
def listar_disponibilidades_do_barbeiro(barbeiro_id: int, conn=Depends(get_db)):
    return disponibilidade_service.listar_por_barbeiro(conn, barbeiro_id)


@router.get("/{barbeiro_id}/horarios-ocupados")
def listar_horarios_ocupados_do_barbeiro(
    barbeiro_id: int,
    inicio: datetime,
    fim: datetime,
    conn=Depends(get_db),
):
    return agenda_service.listar_horarios_ocupados(conn, barbeiro_id, inicio, fim)


@router.post(
    "",
    response_model=BarbeiroResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def criar_barbeiro(payload: BarbeiroCreate, conn=Depends(get_db)):
    return barbeiro_service.criar_barbeiro(conn, payload)


@router.post(
    "/completo",
    response_model=BarbeiroCompletoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def criar_barbeiro_completo(payload: BarbeiroCompletoCreate, conn=Depends(get_db)):
    return barbeiro_service.criar_barbeiro_completo(conn, payload)


@router.put(
    "/{barbeiro_id}/completo",
    response_model=BarbeiroCompletoResponse,
    dependencies=[Depends(require_admin)],
)
def atualizar_barbeiro_completo(
    barbeiro_id: int,
    payload: BarbeiroCompletoUpdate,
    conn=Depends(get_db),
):
    return barbeiro_service.atualizar_barbeiro_completo(conn, barbeiro_id, payload)


@router.put(
    "/{barbeiro_id}", response_model=BarbeiroResponse, dependencies=[Depends(require_admin)]
)
def atualizar_barbeiro(barbeiro_id: int, payload: BarbeiroUpdate, conn=Depends(get_db)):
    return barbeiro_service.atualizar_barbeiro(conn, barbeiro_id, payload)


@router.delete(
    "/{barbeiro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def deletar_barbeiro(barbeiro_id: int, conn=Depends(get_db)):
    barbeiro_service.deletar_barbeiro(conn, barbeiro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
