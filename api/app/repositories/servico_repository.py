def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_servico, nome, descricao, preco, duracao_minutos, ativo
            FROM SERVICO
            ORDER BY nome
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_servico, nome, descricao, preco, duracao_minutos, ativo
            FROM SERVICO
            WHERE id_servico = %s
            """,
            (servico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO SERVICO (nome, descricao, preco, duracao_minutos, ativo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["nome"],
                data["descricao"],
                data["preco"],
                data["duracao_minutos"],
                data["ativo"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, servico_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(servico_id)
            cursor.execute(
                f"""
                UPDATE SERVICO
                SET {", ".join(campos)}
                WHERE id_servico = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, servico_id)


def deletar(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM SERVICO
            WHERE id_servico = %s
            """,
            (servico_id,),
        )
    finally:
        cursor.close()


def existe_atendimento_vinculado(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM ATENDIMENTO_SERVICO
            WHERE SERVICO_id_servico = %s
            """,
            (servico_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()
