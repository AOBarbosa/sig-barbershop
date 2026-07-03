def buscar_por_id(conn, telefone_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_telefone, PESSOA_id_pessoa, numero
            FROM TELEFONE
            WHERE id_telefone = %s
            """,
            (telefone_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def listar_por_pessoa(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_telefone, PESSOA_id_pessoa, numero
            FROM TELEFONE
            WHERE PESSOA_id_pessoa = %s
            ORDER BY id_telefone
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
            INSERT INTO TELEFONE (PESSOA_id_pessoa, numero)
            VALUES (%s, %s)
            """,
            (data["PESSOA_id_pessoa"], data["numero"]),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, telefone_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(telefone_id)
            cursor.execute(
                f"""
                UPDATE TELEFONE
                SET {", ".join(campos)}
                WHERE id_telefone = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, telefone_id)


def deletar(conn, telefone_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM TELEFONE
            WHERE id_telefone = %s
            """,
            (telefone_id,),
        )
    finally:
        cursor.close()
