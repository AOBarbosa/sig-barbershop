def criar(conn, *, servico_id: int, preco_anterior, preco_novo, ativo: bool):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_SERVICO (
                SERVICO_id_servico,
                preco_anterior,
                preco_novo,
                ativo
            )
            VALUES (%s, %s, %s, %s)
            """,
            (servico_id, preco_anterior, preco_novo, ativo),
        )
    finally:
        cursor.close()


def listar_por_servico(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_historico, SERVICO_id_servico, preco_anterior, preco_novo, ativo, alterado_em
            FROM HISTORICO_SERVICO
            WHERE SERVICO_id_servico = %s
            ORDER BY alterado_em DESC
            """,
            (servico_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
