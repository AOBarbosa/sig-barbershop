def buscar_por_id(conn, telefone_id: tuple[int, str]):
    pessoa_id, telefone = telefone_id
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT PESSOA_id_pessoa, telefone
            FROM TELEFONE
            WHERE PESSOA_id_pessoa = %s AND telefone = %s
            """,
            (pessoa_id, telefone),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def listar_por_pessoa(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT PESSOA_id_pessoa, telefone
            FROM TELEFONE
            WHERE PESSOA_id_pessoa = %s
            ORDER BY telefone
            """,
            (pessoa_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO TELEFONE (PESSOA_id_pessoa, telefone)
            VALUES (%s, %s)
            """,
            (data["PESSOA_id_pessoa"], data["telefone"]),
        )
        return buscar_por_id(conn, (data["PESSOA_id_pessoa"], data["telefone"]))
    finally:
        cursor.close()


def atualizar(conn, telefone_id: tuple[int, str], data):
    pessoa_id, telefone_atual = telefone_id
    novo_telefone = data.get("telefone", telefone_atual)
    if data:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                UPDATE TELEFONE
                SET telefone = %s
                WHERE PESSOA_id_pessoa = %s AND telefone = %s
                """,
                (novo_telefone, pessoa_id, telefone_atual),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, (pessoa_id, novo_telefone))


def deletar(conn, telefone_id: tuple[int, str]):
    pessoa_id, telefone = telefone_id
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM TELEFONE
            WHERE PESSOA_id_pessoa = %s AND telefone = %s
            """,
            (pessoa_id, telefone),
        )
    finally:
        cursor.close()
