from datetime import date


def criar(
    conn,
    *,
    servico_id: int,
    preco,
    duracao_em_minutos: int,
    pontos_gerados: int,
    data_inicio=None,
    ativo: bool = True,
    data_fim=None,
):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_SERVICO (
                SERVICO_id_servico,
                preco,
                duracao_em_minutos,
                pontos_gerados,
                data_inicio,
                data_fim,
                ativo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                servico_id,
                preco,
                duracao_em_minutos,
                pontos_gerados,
                data_inicio or date.today(),
                data_fim,
                ativo,
            ),
        )
    finally:
        cursor.close()


def encerrar_vigente(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE HISTORICO_SERVICO
            SET data_fim = CURRENT_DATE, ativo = FALSE
            WHERE SERVICO_id_servico = %s
              AND ativo = TRUE
              AND data_fim IS NULL
            """,
            (servico_id,),
        )
    finally:
        cursor.close()


def listar_por_servico(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, SERVICO_id_servico, preco, duracao_em_minutos,
                   pontos_gerados, data_inicio, data_fim, ativo
            FROM HISTORICO_SERVICO
            WHERE SERVICO_id_servico = %s
            ORDER BY data_inicio DESC
            """,
            (servico_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_vigente(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, SERVICO_id_servico, preco, duracao_em_minutos,
                   pontos_gerados, data_inicio, data_fim, ativo
            FROM HISTORICO_SERVICO
            WHERE SERVICO_id_servico = %s
              AND ativo = TRUE
              AND data_fim IS NULL
            ORDER BY data_inicio DESC
            LIMIT 1
            """,
            (servico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
