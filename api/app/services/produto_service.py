from fastapi import HTTPException

from app.repositories import produto_repository
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate


def listar_produtos(conn):
    return produto_repository.listar(conn)


def buscar_produto(conn, produto_id: int):
    produto = produto_repository.buscar_por_id(conn, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return produto


def criar_produto(conn, payload: ProdutoCreate):
    conn.start_transaction()
    try:
        produto = produto_repository.criar(conn, payload.model_dump())
        conn.commit()
        return produto
    except Exception:
        conn.rollback()
        raise


def atualizar_produto(conn, produto_id: int, payload: ProdutoUpdate):
    conn.start_transaction()
    try:
        if produto_repository.buscar_por_id(conn, produto_id) is None:
            raise HTTPException(status_code=404, detail="Produto nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        produto = produto_repository.atualizar(conn, produto_id, data)
        conn.commit()
        return produto
    except Exception:
        conn.rollback()
        raise


def deletar_produto(conn, produto_id: int):
    conn.start_transaction()
    try:
        if produto_repository.buscar_por_id(conn, produto_id) is None:
            raise HTTPException(status_code=404, detail="Produto nao encontrado")

        if produto_repository.existe_venda_vinculada(conn, produto_id):
            raise HTTPException(
                status_code=409,
                detail="Produto possui movimentacoes vinculadas",
            )

        produto_repository.deletar(conn, produto_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
