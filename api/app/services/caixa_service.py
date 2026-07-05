from fastapi import HTTPException

from app.repositories import caixa_repository, pessoa_repository
from app.schemas.caixa_schema import CaixaCreate


def listar_caixas(conn):
    return caixa_repository.listar(conn)


def buscar_caixa(conn, caixa_id: int):
    caixa = caixa_repository.buscar_por_id(conn, caixa_id)
    if caixa is None:
        raise HTTPException(status_code=404, detail="Caixa nao encontrado")
    return caixa


def criar_caixa(conn, payload: CaixaCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, payload.PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        if caixa_repository.buscar_por_pessoa(conn, payload.PESSOA_id_pessoa) is not None:
            raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como caixa")

        caixa = caixa_repository.criar(conn, payload.model_dump())
        conn.commit()
        return caixa
    except Exception:
        conn.rollback()
        raise


def deletar_caixa(conn, caixa_id: int):
    conn.start_transaction()
    try:
        if caixa_repository.buscar_por_id(conn, caixa_id) is None:
            raise HTTPException(status_code=404, detail="Caixa nao encontrado")

        if caixa_repository.existe_venda_vinculada(conn, caixa_id):
            raise HTTPException(
                status_code=409,
                detail="Caixa possui vendas vinculadas",
            )

        caixa_repository.deletar(conn, caixa_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
