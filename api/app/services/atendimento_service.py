from decimal import Decimal

from fastapi import HTTPException

from app.repositories import (
    agenda_repository,
    atendimento_repository,
    disponibilidade_repository,
)
from app.schemas.atendimento_schema import (
    AtendimentoCreate,
    AtendimentoStatusUpdate,
    AtendimentoUpdate,
)
from app.services import atendimento_servico_service, historico_pontos_service

adicionar_servico_atendimento = atendimento_servico_service.adicionar_servico_atendimento
listar_servicos_atendimento = atendimento_servico_service.listar_servicos_atendimento
remover_servico_atendimento = atendimento_servico_service.remover_servico_atendimento


def listar_atendimentos(conn):
    return atendimento_repository.listar(conn)


def buscar_atendimento(conn, atendimento_id: int):
    atendimento = atendimento_repository.buscar_por_id(conn, atendimento_id)
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    return atendimento


def _validar_cliente(conn, cliente_id: int):
    if not agenda_repository.cliente_existe(conn, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")


def _validar_barbeiro(conn, barbeiro_id: int):
    if not agenda_repository.barbeiro_existe(conn, barbeiro_id):
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")


def _validar_horario_barbeiro(conn, barbeiro_id: int, data_hora_inicio, atendimento_id=None):
    disponivel = disponibilidade_repository.barbeiro_disponivel_no_horario(
        conn, barbeiro_id, data_hora_inicio
    )
    if not disponivel:
        raise HTTPException(
            status_code=422,
            detail="Horario fora da disponibilidade do barbeiro",
        )

    ocupado = agenda_repository.barbeiro_ocupado_no_horario(
        conn, barbeiro_id, data_hora_inicio, atendimento_id
    )
    if ocupado:
        raise HTTPException(
            status_code=409,
            detail="Horario indisponivel para este barbeiro",
        )


def _recalcular_valor_total(conn, atendimento_id: int):
    valor_total = atendimento_repository.calcular_valor_total(conn, atendimento_id)
    return atendimento_repository.atualizar_valor_total(conn, atendimento_id, valor_total)


def criar_atendimento(conn, payload: AtendimentoCreate):
    conn.start_transaction()
    try:
        _validar_cliente(conn, payload.CLIENTE_PESSOA_id_pessoa)
        _validar_barbeiro(conn, payload.BARBEIRO_PESSOA_id_pessoa)
        _validar_horario_barbeiro(conn, payload.BARBEIRO_PESSOA_id_pessoa, payload.data_hora_inicio)

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
        atual = atendimento_repository.buscar_por_id(conn, atendimento_id)
        if atual is None:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        if "CLIENTE_PESSOA_id_pessoa" in data:
            _validar_cliente(conn, data["CLIENTE_PESSOA_id_pessoa"])
        barbeiro_id = data.get("BARBEIRO_PESSOA_id_pessoa", atual["BARBEIRO_PESSOA_id_pessoa"])
        if "BARBEIRO_PESSOA_id_pessoa" in data:
            _validar_barbeiro(conn, barbeiro_id)
        if "data_hora_inicio" in data or "BARBEIRO_PESSOA_id_pessoa" in data:
            data_hora_inicio = data.get("data_hora_inicio", atual["data_hora_inicio"])
            _validar_horario_barbeiro(conn, barbeiro_id, data_hora_inicio, atendimento_id)

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
        atendimento_atual = atendimento_repository.buscar_por_id(conn, atendimento_id)
        if atendimento_atual is None:
            raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

        atendimento = atendimento_repository.atualizar_status(conn, atendimento_id, payload.status)

        if payload.status == "CONCLUIDO" and atendimento_atual["status"] != "CONCLUIDO":
            historico_pontos_service.acumular_pontos_atendimento(
                conn,
                atendimento_id,
                atendimento_atual["CLIENTE_PESSOA_id_pessoa"],
            )

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
