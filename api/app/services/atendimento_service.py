from decimal import Decimal

from fastapi import HTTPException

from app.repositories import atendimento_repository, atendimento_servico_repository, servico_repository
from app.schemas.atendimento_schema import (
    AtendimentoCreate,
    AtendimentoServicoCreate,
    AtendimentoStatusUpdate,
    AtendimentoUpdate,
)


def listar_atendimentos(conn):
    return atendimento_repository.listar(conn)


def buscar_atendimento(conn, atendimento_id: int):
    atendimento = atendimento_repository.buscar_por_id(conn, atendimento_id)
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return atendimento


def listar_servicos_atendimento(conn, atendimento_id: int):
    if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return atendimento_servico_repository.listar_por_atendimento(conn, atendimento_id)


def _validar_atendimento_existe(conn, atendimento_id: int):
    if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")


def _validar_cliente(conn, cliente_id: int):
    if not atendimento_repository.cliente_existe(conn, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")


def _validar_barbeiro(conn, barbeiro_id: int):
    if not atendimento_repository.barbeiro_existe(conn, barbeiro_id):
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")


def _recalcular_valor_total(conn, atendimento_id: int):
    valor_total = atendimento_repository.calcular_valor_total(conn, atendimento_id)
    return atendimento_repository.atualizar_valor_total(conn, atendimento_id, valor_total)


def _buscar_servico(conn, servico_id: int):
    servico = servico_repository.buscar_por_id(conn, servico_id)
    if servico is None:
        raise HTTPException(status_code=404, detail="Servico nao encontrado")
    return servico


def _buscar_vinculo_atendimento_servico(conn, atendimento_id: int, servico_id: int):
    vinculo = atendimento_servico_repository.buscar_por_ids(conn, atendimento_id, servico_id)
    if vinculo is None:
        raise HTTPException(status_code=404, detail="Servico nao vinculado ao atendimento")
    return vinculo


def _validar_servico_disponivel_para_atendimento(conn, atendimento_id: int, servico_id: int):
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
        servico = _buscar_servico(conn, payload.SERVICO_id_servico)
        _validar_servico_disponivel_para_atendimento(conn, atendimento_id, payload.SERVICO_id_servico)
        vinculo = atendimento_servico_repository.criar(
            conn,
            atendimento_id=atendimento_id,
            servico_id=payload.SERVICO_id_servico,
            preco_cobrado=servico["preco"],
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


def criar_atendimento(conn, payload: AtendimentoCreate):
    conn.start_transaction()
    try:
        _validar_cliente(conn, payload.CLIENTE_id_cliente)
        _validar_barbeiro(conn, payload.BARBEIRO_id_barbeiro)

        data = payload.model_dump()
        data["valor_total"] = Decimal("0.00")
        atendimento = atendimento_repository.criar(conn, data)
        atendimento = _recalcular_valor_total(conn, atendimento["id_atendimento"])
        conn.commit()
        return atendimento
    except Exception:
        conn.rollback()
        raise


def atualizar_atendimento(conn, atendimento_id: int, payload: AtendimentoUpdate):
    conn.start_transaction()
    try:
        if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        if "CLIENTE_id_cliente" in data:
            _validar_cliente(conn, data["CLIENTE_id_cliente"])
        if "BARBEIRO_id_barbeiro" in data:
            _validar_barbeiro(conn, data["BARBEIRO_id_barbeiro"])

        atendimento_repository.atualizar(conn, atendimento_id, data)
        atendimento = _recalcular_valor_total(conn, atendimento_id)
        conn.commit()
        return atendimento
    except Exception:
        conn.rollback()
        raise


def atualizar_status_atendimento(
    conn,
    atendimento_id: int,
    payload: AtendimentoStatusUpdate,
):
    conn.start_transaction()
    try:
        if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

        atendimento = atendimento_repository.atualizar_status(conn, atendimento_id, payload.status)
        conn.commit()
        return atendimento
    except Exception:
        conn.rollback()
        raise


def deletar_atendimento(conn, atendimento_id: int):
    conn.start_transaction()
    try:
        if atendimento_repository.buscar_por_id(conn, atendimento_id) is None:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

        atendimento_repository.deletar(conn, atendimento_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
