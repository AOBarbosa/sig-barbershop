def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT PESSOA_id_pessoa FROM CAIXA ORDER BY PESSOA_id_pessoa")
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, caixa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT PESSOA_id_pessoa FROM CAIXA WHERE PESSOA_id_pessoa = %s", (caixa_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_pessoa(conn, pessoa_id: int):
    return buscar_por_id(conn, pessoa_id)


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT INTO CAIXA (PESSOA_id_pessoa) VALUES (%s)",
            (data["PESSOA_id_pessoa"],),
        )
        return buscar_por_id(conn, data["PESSOA_id_pessoa"])
    finally:
        cursor.close()


def deletar(conn, caixa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("DELETE FROM CAIXA WHERE PESSOA_id_pessoa = %s", (caixa_id,))
    finally:
        cursor.close()


def existe_venda_vinculada(conn, caixa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM VENDA WHERE CAIXA_PESSOA_id_pessoa = %s",
            (caixa_id,),
        )
        row = cursor.fetchone()
        return bool(row and row["total"] > 0)
    finally:
        cursor.close()
