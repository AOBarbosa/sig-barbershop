def listar(conn):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_pessoa, nome, cpf, email, data_nascimento, created_at, updated_at
            FROM PESSOA
            ORDER BY nome
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_por_id(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_pessoa, nome, cpf, email, data_nascimento, created_at, updated_at
            FROM PESSOA
            WHERE id_pessoa = %s
            """,
            (pessoa_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_cpf(conn, cpf: str):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_pessoa, nome, cpf, email, data_nascimento, created_at, updated_at
            FROM PESSOA
            WHERE cpf = %s
            """,
            (cpf,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def buscar_por_email(conn, email: str):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id_pessoa, nome, cpf, email, data_nascimento, created_at, updated_at
            FROM PESSOA
            WHERE email = %s
            """,
            (email,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def criar(conn, data):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO PESSOA (nome, cpf, email, data_nascimento)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["nome"],
                data["cpf"],
                data.get("email"),
                data.get("data_nascimento"),
            ),
        )
        return buscar_por_id(conn, cursor.lastrowid)
    finally:
        cursor.close()


def atualizar(conn, pessoa_id: int, data):
    campos = []
    valores = []
    for campo, valor in data.items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if campos:
        cursor = conn.cursor(dictionary=True)
        try:
            valores.append(pessoa_id)
            cursor.execute(
                f"""
                UPDATE PESSOA
                SET {", ".join(campos)}
                WHERE id_pessoa = %s
                """,
                tuple(valores),
            )
        finally:
            cursor.close()

    return buscar_por_id(conn, pessoa_id)


def deletar(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            DELETE FROM PESSOA
            WHERE id_pessoa = %s
            """,
            (pessoa_id,),
        )
    finally:
        cursor.close()


def existe_vinculo(conn, pessoa_id: int):
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM CLIENTE  WHERE PESSOA_id_pessoa = %s) AS clientes,
                (SELECT COUNT(*) FROM BARBEIRO WHERE PESSOA_id_pessoa = %s) AS barbeiros,
                (SELECT COUNT(*) FROM CAIXA    WHERE PESSOA_id_pessoa = %s) AS caixas
            """,
            (pessoa_id, pessoa_id, pessoa_id),
        )
        row = cursor.fetchone()
        if not row:
            return False
        return bool(row["clientes"] + row["barbeiros"] + row["caixas"])
    finally:
        cursor.close()
