from datetime import date


def criar(
    conn,
    *,
    produto_id: int,
    preco_venda,
    preco_custo,
    pontos_gerados: int,
    data_inicio=None,
    ativo: bool = True,
    data_fim=None,
):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_PRODUTO (
                PRODUTO_id_produto,
                preco_venda,
                preco_custo,
                pontos_gerados,
                data_inicio,
                data_fim,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                produto_id,
                preco_venda,
                preco_custo,
                pontos_gerados,
                data_inicio or date.today(),
                data_fim,
                ativo,
            ),
        )
    finally:
        cursor.close()


def encerrar_vigente(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE HISTORICO_PRODUTO
            SET data_fim = CURRENT_DATE, ativo = FALSE
            WHERE PRODUTO_id_produto = %s
              AND ativo = TRUE
              AND data_fim IS NULL
            """,
            (produto_id,),
        )
    finally:
        cursor.close()


def listar_por_produto(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, PRODUTO_id_produto, preco_venda, preco_custo,
                   pontos_gerados, data_inicio, data_fim, ativo
            FROM HISTORICO_PRODUTO
            WHERE PRODUTO_id_produto = %s
            ORDER BY data_inicio DESC
            """,
            (produto_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_vigente(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, PRODUTO_id_produto, preco_venda, preco_custo,
                   pontos_gerados, data_inicio, data_fim, ativo
            FROM HISTORICO_PRODUTO
            WHERE PRODUTO_id_produto = %s
              AND ativo = TRUE
              AND data_fim IS NULL
            ORDER BY data_inicio DESC
            LIMIT 1
            """,
            (produto_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
