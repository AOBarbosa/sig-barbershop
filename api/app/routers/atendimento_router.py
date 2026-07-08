from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_current_user, get_db, require_funcionario
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


def _validar_dono_do_atendimento(usuario: dict, atendimento: dict) -> None:
    if usuario["role"] == "cliente" and atendimento["CLIENTE_PESSOA_id_pessoa"] != usuario["id_pessoa"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito ao proprio cliente ou a funcionarios",
        )


@router.get("", response_model=list[AtendimentoResponse])
def listar_atendimentos(usuario=Depends(get_current_user), conn=Depends(get_db)):
    atendimentos = atendimento_service.listar_atendimentos(conn)
    if usuario["role"] == "cliente":
        return [
            a for a in atendimentos if a["CLIENTE_PESSOA_id_pessoa"] == usuario["id_pessoa"]
        ]
    return atendimentos


@router.get("/{atendimento_id}", response_model=AtendimentoResponse)
def buscar_atendimento(
    atendimento_id: int, usuario=Depends(get_current_user), conn=Depends(get_db)
):
    atendimento = atendimento_service.buscar_atendimento(conn, atendimento_id)
    _validar_dono_do_atendimento(usuario, atendimento)
    return atendimento


@router.get("/{atendimento_id}/servicos", response_model=list[AtendimentoServicoResponse])
def listar_servicos_atendimento(
    atendimento_id: int, usuario=Depends(get_current_user), conn=Depends(get_db)
):
    atendimento = atendimento_service.buscar_atendimento(conn, atendimento_id)
    _validar_dono_do_atendimento(usuario, atendimento)
    return atendimento_service.listar_servicos_atendimento(conn, atendimento_id)


@router.post(
    "/{atendimento_id}/servicos",
    response_model=AtendimentoServicoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_funcionario)],
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
    dependencies=[Depends(require_funcionario)],
)
def remover_servico_atendimento(
    atendimento_id: int,
    servico_id: int,
    conn=Depends(get_db),
):
    atendimento_service.remover_servico_atendimento(conn, atendimento_id, servico_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("", response_model=AtendimentoResponse, status_code=status.HTTP_201_CREATED)
def criar_atendimento(
    payload: AtendimentoCreate, usuario=Depends(get_current_user), conn=Depends(get_db)
):
    if usuario["role"] == "cliente" and payload.CLIENTE_PESSOA_id_pessoa != usuario["id_pessoa"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cliente so pode agendar atendimento para si mesmo",
        )
    return atendimento_service.criar_atendimento(conn, payload)


@router.put(
    "/{atendimento_id}",
    response_model=AtendimentoResponse,
    dependencies=[Depends(require_funcionario)],
)
def atualizar_atendimento(
    atendimento_id: int,
    payload: AtendimentoUpdate,
    conn=Depends(get_db),
):
    return atendimento_service.atualizar_atendimento(conn, atendimento_id, payload)


@router.patch(
    "/{atendimento_id}/status",
    response_model=AtendimentoResponse,
    dependencies=[Depends(require_funcionario)],
)
def atualizar_status_atendimento(
    atendimento_id: int,
    payload: AtendimentoStatusUpdate,
    conn=Depends(get_db),
):
    return atendimento_service.atualizar_status_atendimento(conn, atendimento_id, payload)


@router.delete(
    "/{atendimento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_funcionario)],
)
def deletar_atendimento(atendimento_id: int, conn=Depends(get_db)):
    atendimento_service.deletar_atendimento(conn, atendimento_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
