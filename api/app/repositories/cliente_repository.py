def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_cliente, PESSOA_id_pessoa
            FROM CLIENTE
            ORDER BY id_cliente
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_cliente, PESSOA_id_pessoa
            FROM CLIENTE
            WHERE id_cliente = %s
            """,
            (cliente_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_pessoa(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_cliente, PESSOA_id_pessoa
            FROM CLIENTE
            WHERE PESSOA_id_pessoa = %s
            """,
            (pessoa_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO CLIENTE (PESSOA_id_pessoa)
            VALUES (%s)
            """,
            (data["PESSOA_id_pessoa"],),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def deletar(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM CLIENTE
            WHERE id_cliente = %s
            """,
            (cliente_id,),
        )
    finally:
        cursor.close()


def existe_vinculo(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM ATENDIMENTO      WHERE CLIENTE_id_cliente = %s) AS atendimentos,
                (SELECT COUNT(*) FROM VENDA            WHERE CLIENTE_id_cliente = %s) AS vendas,
                (SELECT COUNT(*) FROM HISTORICO_PONTOS WHERE CLIENTE_id_cliente = %s) AS pontos
            """,
            (cliente_id, cliente_id, cliente_id),
        )
        row = cursor.fetchone()
        if not row:
            return False
        return bool(row["atendimentos"] + row["vendas"] + row["pontos"])
    finally:
        cursor.close()
