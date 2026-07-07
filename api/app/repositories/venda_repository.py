from decimal import Decimal


VENDA_SELECT = """
SELECT
    id_venda,
    CLIENTE_id_cliente,
    CAIXA_id_caixa,
    data_venda,
    valor_total,
    status,
    forma_pagamento
FROM VENDA
"""


def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {VENDA_SELECT}
            ORDER BY data_venda DESC, id_venda DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, venda_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {VENDA_SELECT}
            WHERE id_venda = %s
            """,
            (venda_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO VENDA (
                CLIENTE_id_cliente,
                CAIXA_id_caixa,
                valor_total,
                status,
                forma_pagamento
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["CLIENTE_id_cliente"],
                data["CAIXA_id_caixa"],
                data["valor_total"],
                data["status"],
                data["forma_pagamento"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar_status(conn, venda_id: int, status: str):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE VENDA
            SET status = %s
            WHERE id_venda = %s
            """,
            (status, venda_id),
        )
    finally:
        cursor.close()

    return buscar_por_id(conn, venda_id)


def deletar(conn, venda_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM VENDA
            WHERE id_venda = %s
            """,
            (venda_id,),
        )
    finally:
        cursor.close()


def cliente_existe(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM CLIENTE
            WHERE id_cliente = %s
            """,
            (cliente_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()


def caixa_existe(conn, caixa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM CAIXA
            WHERE id_caixa = %s
            """,
            (caixa_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()


def calcular_valor_total(conn, venda_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(quantidade * preco_unitario), 0.00) AS valor_total
            FROM VENDA_PRODUTO
            WHERE VENDA_id_venda = %s
            """,
            (venda_id,),
        )
        row = cursor.fetchone()
        return row["valor_total"] if row else Decimal("0.00")
    finally:
        cursor.close()


def atualizar_valor_total(conn, venda_id: int, valor_total):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            UPDATE VENDA
            SET valor_total = %s
            WHERE id_venda = %s
            """,
            (valor_total, venda_id),
        )
    finally:
        cursor.close()

    return buscar_por_id(conn, venda_id)
