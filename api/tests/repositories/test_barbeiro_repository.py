import inspect

from app.repositories import barbeiro_repository


class FakeCursor:
    def __init__(self, rows=None, row=None, lastrowid=1):
        self.rows = rows or []
        self.row = row
        self.lastrowid = lastrowid
        self.statements = []
        self.closed = False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.row

    def close(self):
        self.closed = True


class FakeConn:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.cursor_kwargs = None

    def cursor(self, **kwargs):
        self.cursor_kwargs = kwargs
        return self.fake_cursor


def barb_row(barb_id=1):
    return {
        "id_barbeiro": barb_id,
        "PESSOA_id_pessoa": 1,
        "apelido": "Corte masculino",
        "comissao_percentual": 1,
    }


def test_listar_barbeiros():
    cursor = FakeCursor(rows=[barb_row()])
    conn = FakeConn(cursor)

    result = barbeiro_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM BARBEIRO" in cursor.statements[0][0]
    assert len(result) == 1


def test_buscar_por_id():
    cursor = FakeCursor(row=barb_row(3))
    conn = FakeConn(cursor)

    result = barbeiro_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert params == (3,)
    assert result["id_barbeiro"] == 3


def test_buscar_por_pessoa():
    cursor = FakeCursor(row=barb_row())
    conn = FakeConn(cursor)

    result = barbeiro_repository.buscar_por_pessoa(conn, 5)

    sql, params = cursor.statements[0]
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert params == (5,)
    assert result is not None


def test_criar_barbeiro_insere_e_retorna_registro():
    created = barb_row(10)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = barbeiro_repository.criar(
        conn,
        {"PESSOA_id_pessoa": 1, "apelido": "Barba", "comissao_percentual": 10.0},
    )

    insert_sql, insert_params = cursor.statements[0]
    assert "INSERT INTO BARBEIRO" in insert_sql
    assert insert_params == (1, "Barba", 10.0)
    assert result == created


def test_criar_barbeiro_usa_defaults_quando_faltarem_campos():
    cursor = FakeCursor(row=barb_row(), lastrowid=1)
    conn = FakeConn(cursor)

    barbeiro_repository.criar(conn, {"PESSOA_id_pessoa": 1})

    _, insert_params = cursor.statements[0]
    assert insert_params == (1, None, None)


def test_atualizar_barbeiro_apenas_campos_recebidos():
    updated = barb_row() | {"apelido": "Degradê"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = barbeiro_repository.atualizar(conn, 1, {"apelido": "Degradê"})

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE BARBEIRO" in update_sql
    assert "apelido = %s" in update_sql
    assert "comissao_percentual = %s" not in update_sql
    assert update_params == ("Degradê", 1)
    assert result == updated


def test_atualizar_barbeiro_sem_campos_nao_executa_update():
    cursor = FakeCursor(row=barb_row())
    conn = FakeConn(cursor)

    barbeiro_repository.atualizar(conn, 1, {})

    assert len(cursor.statements) == 1
    assert "SELECT" in cursor.statements[0][0]


def test_deletar_barbeiro():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    barbeiro_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM BARBEIRO" in sql
    assert params == (8,)


def test_existe_atendimento_vinculado_true():
    cursor = FakeCursor(row={"total": 2})
    conn = FakeConn(cursor)

    result = barbeiro_repository.existe_atendimento_vinculado(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM ATENDIMENTO" in sql
    assert params == (3,)
    assert result is True


def test_existe_atendimento_vinculado_false():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    assert barbeiro_repository.existe_atendimento_vinculado(conn, 3) is False


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(barbeiro_repository)
    assert "HTTPException" not in source
