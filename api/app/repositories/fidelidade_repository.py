FIDELIDADE_SELECT = """
SELECT id_fidelidade, SERVICO_id_servico, PRODUTO_id_produto,
       pontos_acumulados, pontos_uso, ativo
FROM FIDELIDADE
"""


def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"{FIDELIDADE_SELECT} ORDER BY id_fidelidade")
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, fidelidade_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"{FIDELIDADE_SELECT} WHERE id_fidelidade = %s", (fidelidade_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_servico(conn, servico_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"{FIDELIDADE_SELECT} WHERE SERVICO_id_servico = %s AND ativo = TRUE",
            (servico_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_produto(conn, produto_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            f"{FIDELIDADE_SELECT} WHERE PRODUTO_id_produto = %s AND ativo = TRUE",
            (produto_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO FIDELIDADE (
                SERVICO_id_servico, PRODUTO_id_produto,
                pontos_acumulados, pontos_uso, ativo
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["SERVICO_id_servico"],
                data["PRODUTO_id_produto"],
                data["pontos_acumulados"],
                data["pontos_uso"],
                data["ativo"],
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, fidelidade_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(fidelidade_id)
            cursor.execute(
                f"UPDATE FIDELIDADE SET {', '.join(campos)} WHERE id_fidelidade = %s",
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, fidelidade_id)


def deletar(conn, fidelidade_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM FIDELIDADE WHERE id_fidelidade = %s", (fidelidade_id,))
    finally:
        cursor.close()
