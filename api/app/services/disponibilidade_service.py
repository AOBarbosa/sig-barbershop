from fastapi import HTTPException

from app.repositories import barbeiro_repository, disponibilidade_repository
from app.schemas.disponibilidade_schema import DisponibilidadeCreate, DisponibilidadeUpdate


def buscar_disponibilidade(conn, disponibilidade_id: int):
    disp = disponibilidade_repository.buscar_por_id(conn, disponibilidade_id)
    if disp is None:
        raise HTTPException(status_code=404, detail="Disponibilidade nao encontrada")
    return disp


def listar_por_barbeiro(conn, barbeiro_id: int):
    if barbeiro_repository.buscar_por_id(conn, barbeiro_id) is None:
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")
    return disponibilidade_repository.listar_por_barbeiro(conn, barbeiro_id)


def criar_disponibilidade(conn, payload: DisponibilidadeCreate):
    conn.start_transaction()
    try:
        if barbeiro_repository.buscar_por_id(conn, payload.BARBEIRO_PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        existente = disponibilidade_repository.buscar_por_barbeiro_e_dia(
            conn, payload.BARBEIRO_PESSOA_id_pessoa, payload.dia_semana.value
        )
        if existente is not None:
            raise HTTPException(
                status_code=409,
                detail="Barbeiro ja possui disponibilidade cadastrada para este dia",
            )

        data = payload.model_dump()
        data["dia_semana"] = payload.dia_semana.value
        disp = disponibilidade_repository.criar(conn, data)
        conn.commit()
        return disp
    except Exception:
        conn.rollback()
        raise


def _normalizar_dia_semana(data):
    if "dia_semana" not in data:
        return

    dia_semana = data["dia_semana"]
    data["dia_semana"] = dia_semana.value if hasattr(dia_semana, "value") else dia_semana


def _validar_conflito_dia(conn, disponibilidade_id: int, barbeiro_id: int, dia_semana: str):
    conflito = disponibilidade_repository.buscar_por_barbeiro_e_dia(
        conn, barbeiro_id, dia_semana
    )
    if conflito is not None and conflito["id_disponibilidade"] != disponibilidade_id:
        raise HTTPException(
            status_code=409,
            detail="Barbeiro ja possui disponibilidade cadastrada para este dia",
        )


def _validar_horario(hora_inicio, hora_fim):
    if hora_fim <= hora_inicio:
        raise HTTPException(
            status_code=422,
            detail="hora_fim deve ser posterior a hora_inicio",
        )


def atualizar_disponibilidade(conn, disponibilidade_id: int, payload: DisponibilidadeUpdate):
    conn.start_transaction()
    try:
        atual = disponibilidade_repository.buscar_por_id(conn, disponibilidade_id)
        if atual is None:
            raise HTTPException(status_code=404, detail="Disponibilidade nao encontrada")

        data = payload.model_dump(exclude_unset=True)
        _normalizar_dia_semana(data)

        if "dia_semana" in data and data["dia_semana"] != atual["dia_semana"]:
            _validar_conflito_dia(
                conn,
                disponibilidade_id,
                atual["BARBEIRO_PESSOA_id_pessoa"],
                data["dia_semana"],
            )

        hora_inicio = data.get("hora_inicio", atual["hora_inicio"])
        hora_fim = data.get("hora_fim", atual["hora_fim"])
        _validar_horario(hora_inicio, hora_fim)

        disp = disponibilidade_repository.atualizar(conn, disponibilidade_id, data)
        conn.commit()
        return disp
    except Exception:
        conn.rollback()
        raise


def deletar_disponibilidade(conn, disponibilidade_id: int):
    conn.start_transaction()
    try:
        if disponibilidade_repository.buscar_por_id(conn, disponibilidade_id) is None:
            raise HTTPException(status_code=404, detail="Disponibilidade nao encontrada")

        disponibilidade_repository.deletar(conn, disponibilidade_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
