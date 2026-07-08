def cliente_existe(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM CLIENTE WHERE PESSOA_id_pessoa = %s",
            (cliente_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()


def barbeiro_existe(conn, barbeiro_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM BARBEIRO WHERE PESSOA_id_pessoa = %s",
            (barbeiro_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()


def barbeiro_ocupado_no_horario(
    conn,
    barbeiro_id: int,
    data_hora_inicio,
    atendimento_id: int | None = None,
):
    params = [barbeiro_id, data_hora_inicio]
    filtro_atendimento = ""
    if atendimento_id is not None:
        filtro_atendimento = "AND id_atendimento <> %s"
        params.append(atendimento_id)

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM ATENDIMENTO
            WHERE BARBEIRO_PESSOA_id_pessoa = %s
              AND data_hora_inicio = %s
              AND status <> 'CANCELADO'
              {filtro_atendimento}
            """,
            tuple(params),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()
