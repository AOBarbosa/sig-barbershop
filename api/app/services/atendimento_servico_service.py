from fastapi import HTTPException

from app.repositories import (
    atendimento_repository,
    atendimento_servico_repository,
    historico_servico_repository,
    servico_repository,
)
from app.schemas.atendimento_schema import AtendimentoServicoCreate


def _validar_atendimento_existe(conn, atendimento_id: int):
    if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")


def listar_servicos_atendimento(conn, atendimento_id: int):
    _validar_atendimento_existe(conn, atendimento_id)
    return atendimento_servico_repository.listar_por_atendimento(conn, atendimento_id)


def _recalcular_valor_total(conn, atendimento_id: int):
    valor_total = atendimento_repository.calcular_valor_total(conn, atendimento_id)
    return atendimento_repository.atualizar_valor_total(conn, atendimento_id, valor_total)


def _buscar_servico(conn, servico_id: int):
    servico = servico_repository.buscar_por_id(conn, servico_id)
    if servico is None:
        raise HTTPException(status_code=404, detail="Servico nao encontrado")
    return servico


def _buscar_historico_servico_vigente(conn, servico_id: int):
    historico = historico_servico_repository.buscar_vigente(conn, servico_id)
    if historico is None:
        raise HTTPException(status_code=422, detail="Servico sem preco vigente")
    return historico


def _buscar_vinculo_atendimento_servico(conn, atendimento_id: int, servico_id: int):
    vinculo = atendimento_servico_repository.buscar_por_ids(conn, atendimento_id, servico_id)
    if vinculo is None:
        raise HTTPException(status_code=404, detail="Servico nao vinculado ao atendimento")
    return vinculo


def _validar_servico_disponivel(conn, atendimento_id: int, servico_id: int):
    vinculo = atendimento_servico_repository.buscar_por_ids(conn, atendimento_id, servico_id)
    if vinculo is not None:
        raise HTTPException(status_code=409, detail="Servico ja vinculado ao atendimento")


def adicionar_servico_atendimento(
    conn,
    atendimento_id: int,
    payload: AtendimentoServicoCreate,
):
    conn.start_transaction()
    try:
        _validar_atendimento_existe(conn, atendimento_id)
        _buscar_servico(conn, payload.SERVICO_id_servico)
        _validar_servico_disponivel(conn, atendimento_id, payload.SERVICO_id_servico)
        historico = _buscar_historico_servico_vigente(conn, payload.SERVICO_id_servico)
        vinculo = atendimento_servico_repository.criar(
            conn,
            atendimento_id=atendimento_id,
            servico_id=payload.SERVICO_id_servico,
            preco_cobrado=historico["preco"],
        )
        _recalcular_valor_total(conn, atendimento_id)
        conn.commit()
        return vinculo
    except Exception:
        conn.rollback()
        raise


def remover_servico_atendimento(conn, atendimento_id: int, servico_id: int):
    conn.start_transaction()
    try:
        _validar_atendimento_existe(conn, atendimento_id)
        _buscar_vinculo_atendimento_servico(conn, atendimento_id, servico_id)
        atendimento_servico_repository.deletar_por_ids(conn, atendimento_id, servico_id)
        _recalcular_valor_total(conn, atendimento_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
