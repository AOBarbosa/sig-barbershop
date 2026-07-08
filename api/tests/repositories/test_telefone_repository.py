import inspect

from app.repositories import telefone_repository


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


def tel_row(pessoa_id=1, telefone="84999999999"):
    return {"PESSOA_id_pessoa": pessoa_id, "telefone": telefone}


def test_buscar_por_id_consulta_telefone():
    cursor = FakeCursor(row=tel_row(3))
    conn = FakeConn(cursor)

    result = telefone_repository.buscar_por_id(conn, (3, "84999999999"))

    sql, params = cursor.statements[0]
    assert "FROM TELEFONE" in sql
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert "AND telefone = %s" in sql
    assert params == (3, "84999999999")
    assert result["PESSOA_id_pessoa"] == 3


def test_listar_por_pessoa_filtra_por_pessoa():
    cursor = FakeCursor(rows=[tel_row()])
    conn = FakeConn(cursor)

    result = telefone_repository.listar_por_pessoa(conn, 1)

    sql, params = cursor.statements[0]
    assert "WHERE PESSOA_id_pessoa = %s" in sql
    assert params == (1,)
    assert len(result) == 1


def test_criar_telefone_insere_e_retorna_registro():
    created = tel_row()
    cursor = FakeCursor(row=created)
    conn = FakeConn(cursor)

    result = telefone_repository.criar(
        conn, {"PESSOA_id_pessoa": 1, "telefone": "84999999999"}
    )

    insert_sql, insert_params = cursor.statements[0]
    assert "INSERT INTO TELEFONE" in insert_sql
    assert insert_params == (1, "84999999999")
    assert result == created


def test_atualizar_telefone_apenas_campos_recebidos():
    updated = tel_row() | {"telefone": "84988888888"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = telefone_repository.atualizar(conn, (1, "84999999999"), {"telefone": "84988888888"})

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE TELEFONE" in update_sql
    assert "telefone = %s" in update_sql
    assert update_params == ("84988888888", 1, "84999999999")
    assert result == updated


def test_atualizar_telefone_sem_campos_nao_executa_update():
    cursor = FakeCursor(row=tel_row())
    conn = FakeConn(cursor)

    telefone_repository.atualizar(conn, (1, "84999999999"), {})

    assert len(cursor.statements) == 1
    assert "SELECT" in cursor.statements[0][0]


def test_deletar_telefone_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    telefone_repository.deletar(conn, (5, "84999999999"))

    sql, params = cursor.statements[0]
    assert "DELETE FROM TELEFONE" in sql
    assert params == (5, "84999999999")


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(telefone_repository)
    assert "HTTPException" not in source
