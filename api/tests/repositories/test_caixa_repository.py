import inspect

from app.repositories import caixa_repository


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


def caixa_row(caixa_id=1, pessoa_id=1):
    return {"id_caixa": caixa_id, "PESSOA_id_pessoa": pessoa_id}


def test_listar_caixas_retorna_linhas():
    cursor = FakeCursor(rows=[caixa_row()])
    conn = FakeConn(cursor)

    result = caixa_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM CAIXA" in cursor.statements[0][0]
    assert len(result) == 1


def test_buscar_por_id():
    cursor = FakeCursor(row=caixa_row(3))
    conn = FakeConn(cursor)

    result = caixa_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert params == (3,)
    assert result["id_caixa"] == 3


def test_buscar_por_pessoa():
    cursor = FakeCursor(row=caixa_row(pessoa_id=5))
    conn = FakeConn(cursor)

    result = caixa_repository.buscar_por_pessoa(conn, 5)

    sql, params = cursor.statements[0]
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert params == (5,)
    assert result is not None


def test_criar_caixa_insere_e_retorna_registro():
    created = caixa_row(caixa_id=10, pessoa_id=7)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = caixa_repository.criar(conn, {"PESSOA_id_pessoa": 7})

    insert_sql, insert_params = cursor.statements[0]
    assert "INSERT INTO CAIXA" in insert_sql
    assert insert_params == (7,)
    assert result == created


def test_deletar_caixa():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    caixa_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM CAIXA" in sql
    assert params == (8,)


def test_existe_venda_vinculada_true():
    cursor = FakeCursor(row={"total": 2})
    conn = FakeConn(cursor)

    result = caixa_repository.existe_venda_vinculada(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM VENDA" in sql
    assert params == (3,)
    assert result is True


def test_existe_venda_vinculada_false():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    assert caixa_repository.existe_venda_vinculada(conn, 3) is False


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(caixa_repository)
    assert "HTTPException" not in source
