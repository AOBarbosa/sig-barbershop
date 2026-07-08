CLIENTE_SELECT = """
SELECT
    c.PESSOA_id_pessoa,
    c.preferencias,
    c.observacoes,
    COALESCE(
        SUM(
            CASE
                WHEN hp.tipo_movimentacao = 'ACUMULA' THEN hp.pontos
                WHEN hp.tipo_movimentacao = 'USA' THEN -hp.pontos
                ELSE 0
            END
        ),
        0
    ) AS saldo_pontos
FROM CLIENTE c
LEFT JOIN HISTORICO_PONTOS hp
    ON hp.CLIENTE_PESSOA_id_pessoa = c.PESSOA_id_pessoa
"""


def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {CLIENTE_SELECT}
            GROUP BY c.PESSOA_id_pessoa, c.preferencias, c.observacoes
            ORDER BY c.PESSOA_id_pessoa
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"""
            {CLIENTE_SELECT}
            WHERE c.PESSOA_id_pessoa = %s
            GROUP BY c.PESSOA_id_pessoa, c.preferencias, c.observacoes
            """,
            (cliente_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_pessoa(conn, pessoa_id: int):
    return buscar_por_id(conn, pessoa_id)


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO CLIENTE (PESSOA_id_pessoa, preferencias, observacoes)
            VALUES (%s, %s, %s)
            """,
            (
                data["PESSOA_id_pessoa"],
                data.get("preferencias"),
                data.get("observacoes"),
            ),
        )
        return buscar_por_id(conn, data["PESSOA_id_pessoa"])
    finally:
        cursor.close()


def deletar(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM CLIENTE WHERE PESSOA_id_pessoa = %s", (cliente_id,))
    finally:
        cursor.close()


def existe_vinculo(conn, cliente_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM ATENDIMENTO WHERE CLIENTE_PESSOA_id_pessoa = %s) AS atendimentos,
                (SELECT COUNT(*) FROM VENDA WHERE CLIENTE_PESSOA_id_pessoa = %s) AS vendas,
                (SELECT COUNT(*) FROM HISTORICO_PONTOS WHERE CLIENTE_PESSOA_id_pessoa = %s) AS pontos
            """,
            (cliente_id, cliente_id, cliente_id),
        )
        row = cursor.fetchone()
        if not row:
            return False
        return bool(row["atendimentos"] + row["vendas"] + row["pontos"])
    finally:
        cursor.close()
