HISTORICO_PONTOS_SELECT = """
SELECT
    id_historico,
    CLIENTE_id_cliente,
    pontos,
    tipo_movimentacao,
    descricao,
    data_movimentacao
FROM HISTORICO_PONTOS
"""


def listar_por_cliente(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {HISTORICO_PONTOS_SELECT}
            WHERE CLIENTE_id_cliente = %s
            ORDER BY data_movimentacao DESC, id_historico DESC
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
            WHERE id_historico = %s
            """,
            (historico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, cliente_id: int, pontos: int, tipo_movimentacao: str, descricao: str | None):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO HISTORICO_PONTOS (
                CLIENTE_id_cliente,
                pontos,
                tipo_movimentacao,
                descricao
            )
            VALUES (%s, %s, %s, %s)
            """,
            (cliente_id, pontos, tipo_movimentacao, descricao),
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
                SUM(CASE WHEN tipo_movimentacao = 'acumulo' THEN pontos ELSE -pontos END),
                0
            ) AS saldo
            FROM HISTORICO_PONTOS
            WHERE CLIENTE_id_cliente = %s
            """,
            (cliente_id,),
        )
        row = cursor.fetchone()
        return row["saldo"] if row else 0
    finally:
        cursor.close()
