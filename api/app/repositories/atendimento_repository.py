from decimal import Decimal

from app.repositories import agenda_repository


ATENDIMENTO_SELECT = """
SELECT
    id_atendimento,
    CLIENTE_PESSOA_id_pessoa,
    BARBEIRO_PESSOA_id_pessoa,
    data_hora_inicio,
    data_hora_fim,
    status,
    valor_total,
    observacoes
FROM ATENDIMENTO
"""


def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {ATENDIMENTO_SELECT}
            ORDER BY data_hora_inicio DESC, id_atendimento DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, atendimento_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {ATENDIMENTO_SELECT}
            WHERE id_atendimento = %s
            """,
            (atendimento_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO ATENDIMENTO (
                CLIENTE_PESSOA_id_pessoa,
                BARBEIRO_PESSOA_id_pessoa,
                data_hora_inicio,
                data_hora_fim,
                status,
                valor_total,
                observacoes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["CLIENTE_PESSOA_id_pessoa"],
                data["BARBEIRO_PESSOA_id_pessoa"],
                data["data_hora_inicio"],
                data.get("data_hora_fim"),
                data["status"],
                data["valor_total"],
                data["observacoes"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, atendimento_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(atendimento_id)
            cursor.execute(
                f"""
                UPDATE ATENDIMENTO
                SET {", ".join(campos)}
                WHERE id_atendimento = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, atendimento_id)


def atualizar_status(conn, atendimento_id: int, status: str):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE ATENDIMENTO
            SET status = %s
            WHERE id_atendimento = %s
            """,
            (status, atendimento_id),
        )
    finally:
        cursor.close()

    return buscar_por_id(conn, atendimento_id)


def deletar(conn, atendimento_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM ATENDIMENTO
            WHERE id_atendimento = %s
            """,
            (atendimento_id,),
        )
    finally:
        cursor.close()


def cliente_existe(conn, cliente_id: int):
    return agenda_repository.cliente_existe(conn, cliente_id)


def barbeiro_existe(conn, barbeiro_id: int):
    return agenda_repository.barbeiro_existe(conn, barbeiro_id)


def calcular_valor_total(conn, atendimento_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(preco_cobrado), 0.00) AS valor_total
            FROM ATENDIMENTO_SERVICO
            WHERE ATENDIMENTO_id_atendimento = %s
            """,
            (atendimento_id,),
        )
        row = cursor.fetchone()
        return row["valor_total"] if row else Decimal("0.00")
    finally:
        cursor.close()


def atualizar_valor_total(conn, atendimento_id: int, valor_total):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE ATENDIMENTO
            SET valor_total = %s
            WHERE id_atendimento = %s
            """,
            (valor_total, atendimento_id),
        )
    finally:
        cursor.close()

    return buscar_por_id(conn, atendimento_id)
