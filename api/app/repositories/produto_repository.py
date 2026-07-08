def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.id_produto, p.nome, p.categoria, p.ativo,
                   h.preco_venda, h.preco_custo, h.pontos_gerados
            FROM PRODUTO p
            LEFT JOIN HISTORICO_PRODUTO h
              ON h.PRODUTO_id_produto = p.id_produto
             AND h.ativo = TRUE
             AND h.data_fim IS NULL
            ORDER BY nome
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.id_produto, p.nome, p.categoria, p.ativo,
                   h.preco_venda, h.preco_custo, h.pontos_gerados
            FROM PRODUTO p
            LEFT JOIN HISTORICO_PRODUTO h
              ON h.PRODUTO_id_produto = p.id_produto
             AND h.ativo = TRUE
             AND h.data_fim IS NULL
            WHERE p.id_produto = %s
            """,
            (produto_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO PRODUTO (nome, categoria, ativo)
            VALUES (%s, %s, %s)
            """,
            (
                data["nome"],
                data.get("categoria"),
                data["ativo"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, produto_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(produto_id)
            cursor.execute(
                f"""
                UPDATE PRODUTO
                SET {", ".join(campos)}
                WHERE id_produto = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, produto_id)


def deletar(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM PRODUTO
            WHERE id_produto = %s
            """,
            (produto_id,),
        )
    finally:
        cursor.close()


def existe_venda_vinculada(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM VENDA_PRODUTO
            WHERE PRODUTO_id_produto = %s
            """,
            (produto_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()
