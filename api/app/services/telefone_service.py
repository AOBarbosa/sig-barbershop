from fastapi import HTTPException

from app.repositories import pessoa_repository, telefone_repository
from app.schemas.telefone_schema import TelefoneCreate, TelefoneUpdate


def buscar_telefone(conn, pessoa_id: int, telefone_numero: str):
    telefone = telefone_repository.buscar_por_id(conn, (pessoa_id, telefone_numero))
    if telefone is None:
        raise HTTPException(status_code=404, detail="Telefone nao encontrado")
    return telefone


def listar_por_pessoa(conn, pessoa_id: int):
    if pessoa_repository.buscar_por_id(conn, pessoa_id) is None:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return telefone_repository.listar_por_pessoa(conn, pessoa_id)


def criar_telefone(conn, payload: TelefoneCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, payload.PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        telefone = telefone_repository.criar(conn, payload.model_dump())
        conn.commit()
        return telefone
    except Exception:
        conn.rollback()
        raise


def atualizar_telefone(conn, pessoa_id: int, telefone_numero: str, payload: TelefoneUpdate):
    conn.start_transaction()
    try:
        telefone_id = (pessoa_id, telefone_numero)
        if telefone_repository.buscar_por_id(conn, telefone_id) is None:
            raise HTTPException(status_code=404, detail="Telefone nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        telefone = telefone_repository.atualizar(conn, telefone_id, data)
        conn.commit()
        return telefone
    except Exception:
        conn.rollback()
        raise


def deletar_telefone(conn, pessoa_id: int, telefone_numero: str):
    conn.start_transaction()
    try:
        telefone_id = (pessoa_id, telefone_numero)
        if telefone_repository.buscar_por_id(conn, telefone_id) is None:
            raise HTTPException(status_code=404, detail="Telefone nao encontrado")

        telefone_repository.deletar(conn, telefone_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
