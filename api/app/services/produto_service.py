from fastapi import HTTPException

from app.repositories import historico_produto_repository, produto_repository
from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate


def listar_produtos(conn):
    return produto_repository.listar(conn)


def buscar_produto(conn, produto_id: int):
    produto = produto_repository.buscar_por_id(conn, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return produto


def listar_historico_produto(conn, produto_id: int):
    if produto_repository.buscar_por_id(conn, produto_id) is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return historico_produto_repository.listar_por_produto(conn, produto_id)


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
        produto_atual = produto_repository.buscar_por_id(conn, produto_id)
        if produto_atual is None:
            raise HTTPException(status_code=404, detail="Produto nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        produto = produto_repository.atualizar(conn, produto_id, data)
        historico_produto_repository.criar(
            conn,
            produto_id=produto_id,
            preco_anterior=produto_atual["preco"],
            preco_novo=produto["preco"],
            estoque_anterior=produto_atual["estoque"],
            estoque_novo=produto["estoque"],
            ativo=bool(produto["ativo"]),
        )
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
