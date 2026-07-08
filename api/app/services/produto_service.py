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
        data = payload.model_dump()
        produto_data = {
            "nome": data["nome"],
            "categoria": data.get("categoria"),
            "ativo": data["ativo"],
        }
        produto = produto_repository.criar(conn, produto_data)
        historico_produto_repository.criar(
            conn,
            produto_id=produto["id_produto"],
            preco_venda=data["preco_venda"],
            preco_custo=data["preco_custo"],
            pontos_gerados=data["pontos_gerados"],
            ativo=True,
        )
        produto = produto_repository.buscar_por_id(conn, produto["id_produto"])
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
        produto_data = {
            key: data[key]
            for key in ("nome", "categoria", "ativo")
            if key in data
        }
        historico_data = {
            key: data[key]
            for key in ("preco_venda", "preco_custo", "pontos_gerados")
            if key in data
        }

        if produto_data:
            produto_repository.atualizar(conn, produto_id, produto_data)
        if historico_data:
            vigente = historico_produto_repository.buscar_vigente(conn, produto_id) or {}
            novo_historico = {
                "preco_venda": historico_data.get("preco_venda", vigente.get("preco_venda")),
                "preco_custo": historico_data.get("preco_custo", vigente.get("preco_custo")),
                "pontos_gerados": historico_data.get(
                    "pontos_gerados",
                    vigente.get("pontos_gerados", 0),
                ),
            }
            historico_produto_repository.encerrar_vigente(conn, produto_id)
            historico_produto_repository.criar(
                conn,
                produto_id=produto_id,
                ativo=True,
                **novo_historico,
            )

        produto = produto_repository.buscar_por_id(conn, produto_id)
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
