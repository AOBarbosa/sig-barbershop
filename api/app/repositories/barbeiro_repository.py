def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_barbeiro, PESSOA_id_pessoa, especialidade, ativo
            FROM BARBEIRO
            ORDER BY id_barbeiro
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, barbeiro_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_barbeiro, PESSOA_id_pessoa, especialidade, ativo
            FROM BARBEIRO
            WHERE id_barbeiro = %s
            """,
            (barbeiro_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_pessoa(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_barbeiro, PESSOA_id_pessoa, especialidade, ativo
            FROM BARBEIRO
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
            INSERT INTO BARBEIRO (PESSOA_id_pessoa, especialidade, ativo)
            VALUES (%s, %s, %s)
            """,
            (
                data["PESSOA_id_pessoa"],
                data.get("especialidade"),
                data.get("ativo", True),
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, barbeiro_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(barbeiro_id)
            cursor.execute(
                f"""
                UPDATE BARBEIRO
                SET {", ".join(campos)}
                WHERE id_barbeiro = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, barbeiro_id)


def deletar(conn, barbeiro_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM BARBEIRO
            WHERE id_barbeiro = %s
            """,
            (barbeiro_id,),
        )
    finally:
        cursor.close()


def existe_atendimento_vinculado(conn, barbeiro_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM ATENDIMENTO
            WHERE BARBEIRO_id_barbeiro = %s
            """,
            (barbeiro_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()
