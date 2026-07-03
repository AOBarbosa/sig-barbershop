def criar(conn, *, produto_id: int, preco_anterior, preco_novo, estoque_anterior, estoque_novo, ativo: bool):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_PRODUTO (
                PRODUTO_id_produto,
                preco_anterior,
                preco_novo,
                estoque_anterior,
                estoque_novo,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (produto_id, preco_anterior, preco_novo, estoque_anterior, estoque_novo, ativo),
        )
    finally:
        cursor.close()


def listar_por_produto(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, PRODUTO_id_produto, preco_anterior, preco_novo,
                   estoque_anterior, estoque_novo, ativo, alterado_em
            FROM HISTORICO_PRODUTO
            WHERE PRODUTO_id_produto = %s
            ORDER BY alterado_em DESC
            """,
            (produto_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
