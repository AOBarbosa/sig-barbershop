def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_produto, nome, descricao, preco, estoque, ativo
            FROM PRODUTO
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
            SELECT id_produto, nome, descricao, preco, estoque, ativo
            FROM PRODUTO
            WHERE id_produto = %s
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
            INSERT INTO PRODUTO (nome, descricao, preco, estoque, ativo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["nome"],
                data["descricao"],
                data["preco"],
                data["estoque"],
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
