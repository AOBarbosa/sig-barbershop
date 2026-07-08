def buscar_por_id(conn, disponibilidade_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_disponibilidade, BARBEIRO_PESSOA_id_pessoa, dia_semana,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim
            FROM DISPONIBILIDADE
            WHERE id_disponibilidade = %s
            """,
            (disponibilidade_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def listar_por_barbeiro(conn, barbeiro_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_disponibilidade, BARBEIRO_PESSOA_id_pessoa, dia_semana,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim
            FROM DISPONIBILIDADE
            WHERE BARBEIRO_PESSOA_id_pessoa = %s
            ORDER BY FIELD(dia_semana,'SEGUNDA','TERCA','QUARTA','QUINTA','SEXTA','SABADO','DOMINGO')
            """,
            (barbeiro_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_barbeiro_e_dia(conn, barbeiro_id: int, dia_semana: str):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_disponibilidade, BARBEIRO_PESSOA_id_pessoa, dia_semana,
                   CAST(hora_inicio AS CHAR) AS hora_inicio,
                   CAST(hora_fim AS CHAR) AS hora_fim
            FROM DISPONIBILIDADE
            WHERE BARBEIRO_PESSOA_id_pessoa = %s AND dia_semana = %s
            """,
            (barbeiro_id, dia_semana),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def barbeiro_disponivel_no_horario(conn, barbeiro_id: int, data_hora_inicio):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM DISPONIBILIDADE
            WHERE BARBEIRO_PESSOA_id_pessoa = %s
              AND ativo = TRUE
              AND dia_semana = CASE DAYOFWEEK(%s)
                  WHEN 1 THEN 'DOMINGO'
                  WHEN 2 THEN 'SEGUNDA'
                  WHEN 3 THEN 'TERCA'
                  WHEN 4 THEN 'QUARTA'
                  WHEN 5 THEN 'QUINTA'
                  WHEN 6 THEN 'SEXTA'
                  WHEN 7 THEN 'SABADO'
              END
              AND TIME(%s) >= hora_inicio
              AND TIME(%s) < hora_fim
            """,
            (barbeiro_id, data_hora_inicio, data_hora_inicio, data_hora_inicio),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO DISPONIBILIDADE (
                BARBEIRO_PESSOA_id_pessoa, dia_semana, hora_inicio, hora_fim
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["BARBEIRO_PESSOA_id_pessoa"],
                data["dia_semana"],
                data["hora_inicio"],
                data["hora_fim"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, disponibilidade_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(disponibilidade_id)
            cursor.execute(
                f"""
                UPDATE DISPONIBILIDADE
                SET {", ".join(campos)}
                WHERE id_disponibilidade = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, disponibilidade_id)


def deletar(conn, disponibilidade_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM DISPONIBILIDADE
            WHERE id_disponibilidade = %s
            """,
            (disponibilidade_id,),
        )
    finally:
        cursor.close()
