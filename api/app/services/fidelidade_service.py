from fastapi import HTTPException

from app.repositories import fidelidade_repository
from app.schemas.fidelidade_schema import FidelidadeCreate, FidelidadeUpdate


def _validar_xor(servico_id, produto_id):
    if (servico_id is None) == (produto_id is None):
        raise HTTPException(
            status_code=422,
            detail="Fidelidade deve referenciar exatamente um de SERVICO ou PRODUTO",
        )


def listar_fidelidades(conn):
    return fidelidade_repository.listar(conn)


def buscar_fidelidade(conn, fidelidade_id: int):
    fidelidade = fidelidade_repository.buscar_por_id(conn, fidelidade_id)
    if fidelidade is None:
        raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")
    return fidelidade


def criar_fidelidade(conn, payload: FidelidadeCreate):
    conn.start_transaction()
    try:
        _validar_xor(payload.SERVICO_id_servico, payload.PRODUTO_id_produto)
        fidelidade = fidelidade_repository.criar(conn, payload.model_dump())
        conn.commit()
        return fidelidade
    except Exception:
        conn.rollback()
        raise


def atualizar_fidelidade(conn, fidelidade_id: int, payload: FidelidadeUpdate):
    conn.start_transaction()
    try:
        atual = fidelidade_repository.buscar_por_id(conn, fidelidade_id)
        if atual is None:
            raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")

        data = payload.model_dump(exclude_unset=True)
        servico_id = data.get("SERVICO_id_servico", atual["SERVICO_id_servico"])
        produto_id = data.get("PRODUTO_id_produto", atual["PRODUTO_id_produto"])
        _validar_xor(servico_id, produto_id)

        fidelidade = fidelidade_repository.atualizar(conn, fidelidade_id, data)
        conn.commit()
        return fidelidade
    except Exception:
        conn.rollback()
        raise


def deletar_fidelidade(conn, fidelidade_id: int):
    conn.start_transaction()
    try:
        if fidelidade_repository.buscar_por_id(conn, fidelidade_id) is None:
            raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")

        fidelidade_repository.deletar(conn, fidelidade_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
