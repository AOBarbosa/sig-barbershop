VENDA_PRODUTO_SELECT = """
SELECT
    VENDA_id_venda,
    PRODUTO_id_produto,
    quantidade,
    preco_unitario
FROM VENDA_PRODUTO
"""


def listar_por_venda(conn, venda_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {VENDA_PRODUTO_SELECT}
            WHERE VENDA_id_venda = %s
            ORDER BY PRODUTO_id_produto
            """,
            (venda_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, venda_produto_id: tuple[int, int]):
    venda_id, produto_id = venda_produto_id
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {VENDA_PRODUTO_SELECT}
            WHERE VENDA_id_venda = %s
              AND PRODUTO_id_produto = %s
            """,
            (venda_id, produto_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_ids(conn, venda_id: int, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {VENDA_PRODUTO_SELECT}
            WHERE VENDA_id_venda = %s
              AND PRODUTO_id_produto = %s
            """,
            (venda_id, produto_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, venda_id: int, produto_id: int, quantidade: int, preco_unitario):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO VENDA_PRODUTO (
                VENDA_id_venda,
                PRODUTO_id_produto,
                quantidade,
                preco_unitario
            )
            VALUES (%s, %s, %s, %s)
            """,
            (venda_id, produto_id, quantidade, preco_unitario),
        )
        return buscar_por_ids(conn, venda_id, produto_id)
    finally:
        cursor.close()


def deletar_por_ids(conn, venda_id: int, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM VENDA_PRODUTO
            WHERE VENDA_id_venda = %s
              AND PRODUTO_id_produto = %s
            """,
            (venda_id, produto_id),
        )
    finally:
        cursor.close()
