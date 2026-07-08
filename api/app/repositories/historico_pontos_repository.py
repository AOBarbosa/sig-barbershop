HISTORICO_PONTOS_SELECT = """
SELECT
    id_movimentacao,
    CLIENTE_PESSOA_id_pessoa,
    VENDA_id_venda,
    FIDELIDADE_id_fidelidade,
    pontos,
    tipo_movimentacao,
    data_movimentacao
FROM HISTORICO_PONTOS
"""


def listar_por_cliente(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {HISTORICO_PONTOS_SELECT}
            WHERE CLIENTE_PESSOA_id_pessoa = %s
            ORDER BY data_movimentacao DESC, id_movimentacao DESC
            """,
            (cliente_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, historico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {HISTORICO_PONTOS_SELECT}
            WHERE id_movimentacao = %s
            """,
            (historico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(
    conn,
    cliente_id: int,
    venda_id: int,
    fidelidade_id: int,
    pontos: int,
    tipo_movimentacao: str,
):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_PONTOS (
                CLIENTE_PESSOA_id_pessoa,
                VENDA_id_venda,
                FIDELIDADE_id_fidelidade,
                pontos,
                tipo_movimentacao,
                data_movimentacao
            )
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (cliente_id, venda_id, fidelidade_id, pontos, tipo_movimentacao),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def calcular_saldo(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COALESCE(
                SUM(CASE WHEN tipo_movimentacao = 'ACUMULA' THEN pontos ELSE -pontos END),
                0
            ) AS saldo
            FROM HISTORICO_PONTOS
            WHERE CLIENTE_PESSOA_id_pessoa = %s
            """,
            (cliente_id,),
        )
        row = cursor.fetchone()
        return row["saldo"] if row else 0
    finally:
        cursor.close()
