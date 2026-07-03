from fastapi import HTTPException

from app.repositories import barbeiro_repository, pessoa_repository
from app.schemas.barbeiro_schema import BarbeiroCreate, BarbeiroUpdate


def listar_barbeiros(conn):
    return barbeiro_repository.listar(conn)


def buscar_barbeiro(conn, barbeiro_id: int):
    barbeiro = barbeiro_repository.buscar_por_id(conn, barbeiro_id)
    if barbeiro is None:
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")
    return barbeiro


def criar_barbeiro(conn, payload: BarbeiroCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, payload.PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        if barbeiro_repository.buscar_por_pessoa(conn, payload.PESSOA_id_pessoa) is not None:
            raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como barbeiro")

        barbeiro = barbeiro_repository.criar(conn, payload.model_dump())
        conn.commit()
        return barbeiro
    except Exception:
        conn.rollback()
        raise


def atualizar_barbeiro(conn, barbeiro_id: int, payload: BarbeiroUpdate):
    conn.start_transaction()
    try:
        if barbeiro_repository.buscar_por_id(conn, barbeiro_id) is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        barbeiro = barbeiro_repository.atualizar(conn, barbeiro_id, data)
        conn.commit()
        return barbeiro
    except Exception:
        conn.rollback()
        raise


def deletar_barbeiro(conn, barbeiro_id: int):
    conn.start_transaction()
    try:
        if barbeiro_repository.buscar_por_id(conn, barbeiro_id) is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        if barbeiro_repository.existe_atendimento_vinculado(conn, barbeiro_id):
            raise HTTPException(
                status_code=409,
                detail="Barbeiro possui atendimentos vinculados",
            )

        barbeiro_repository.deletar(conn, barbeiro_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
