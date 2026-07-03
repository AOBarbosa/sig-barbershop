ATENDIMENTO_SERVICO_SELECT = """
SELECT
    id_atendimento_servico,
    ATENDIMENTO_id_atendimento,
    SERVICO_id_servico,
    preco_cobrado
FROM ATENDIMENTO_SERVICO
"""


def listar_por_atendimento(conn, atendimento_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {ATENDIMENTO_SERVICO_SELECT}
            WHERE ATENDIMENTO_id_atendimento = %s
            ORDER BY id_atendimento_servico
            """,
            (atendimento_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, atendimento_servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {ATENDIMENTO_SERVICO_SELECT}
            WHERE id_atendimento_servico = %s
            """,
            (atendimento_servico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_ids(conn, atendimento_id: int, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {ATENDIMENTO_SERVICO_SELECT}
            WHERE ATENDIMENTO_id_atendimento = %s
              AND SERVICO_id_servico = %s
            """,
            (atendimento_id, servico_id),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, atendimento_id: int, servico_id: int, preco_cobrado):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO ATENDIMENTO_SERVICO (
                ATENDIMENTO_id_atendimento,
                SERVICO_id_servico,
                preco_cobrado
            )
            VALUES (%s, %s, %s)
            """,
            (atendimento_id, servico_id, preco_cobrado),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def deletar_por_ids(conn, atendimento_id: int, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM ATENDIMENTO_SERVICO
            WHERE ATENDIMENTO_id_atendimento = %s
              AND SERVICO_id_servico = %s
            """,
            (atendimento_id, servico_id),
        )
    finally:
        cursor.close()
