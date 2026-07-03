import inspect

from app.repositories import fidelidade_repository


class FakeCursor:
    def __init__(self, rows=None, row=None, row_queue=None, lastrowid=1):
        self.rows = rows or []
        self.row = row
        self.row_queue = list(row_queue or [])
        self.lastrowid = lastrowid
        self.statements = []
        self.closed = False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def fetchall(self):
        return self.rows

    def fetchone(self):
        if self.row_queue:
            return self.row_queue.pop(0)
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


def fidelidade_row(fidelidade_id=1, servico_id=1, produto_id=None):
    return {
        "id_fidelidade": fidelidade_id,
        "SERVICO_id_servico": servico_id,
        "PRODUTO_id_produto": produto_id,
        "pontos": 10,
        "ativo": 1,
    }


def test_listar_fidelidades_usa_cursor_dictionary_e_retorna_linhas():
    rows = [fidelidade_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = fidelidade_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM FIDELIDADE" in cursor.statements[0][0]
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_fidelidade_por_id():
    cursor = FakeCursor(row=fidelidade_row(fidelidade_id=3))
    conn = FakeConn(cursor)

    result = fidelidade_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM FIDELIDADE" in sql
    assert "WHERE id_fidelidade = %s" in sql
    assert params == (3,)
    assert result["id_fidelidade"] == 3
    assert cursor.closed is True


def test_criar_fidelidade_insere_sql_puro_e_retorna_registro_criado():
    created = fidelidade_row(fidelidade_id=10, servico_id=None, produto_id=5)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = fidelidade_repository.criar(
        conn,
        {
            "SERVICO_id_servico": None,
            "PRODUTO_id_produto": 5,
            "pontos": 10,
            "ativo": True,
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO FIDELIDADE" in insert_sql
    assert insert_params == (None, 5, 10, True)
    assert "FROM FIDELIDADE" in select_sql
    assert select_params == (10,)
    assert result == created
    assert cursor.closed is True


def test_atualizar_fidelidade_executa_update_apenas_dos_campos_recebidos_e_retorna_registro():
    updated = fidelidade_row(fidelidade_id=4) | {"pontos": 20}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = fidelidade_repository.atualizar(conn, 4, {"pontos": 20})

    update_sql, update_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "UPDATE FIDELIDADE" in update_sql
    assert "pontos = %s" in update_sql
    assert "ativo = %s" not in update_sql
    assert update_params == (20, 4)
    assert "FROM FIDELIDADE" in select_sql
    assert select_params == (4,)
    assert result == updated


def test_atualizar_fidelidade_sem_campos_nao_executa_update_e_retorna_registro_atual():
    current = fidelidade_row(fidelidade_id=5)
    cursor = FakeCursor(row=current)
    conn = FakeConn(cursor)

    result = fidelidade_repository.atualizar(conn, 5, {})

    assert len(cursor.statements) == 1
    sql, params = cursor.statements[0]
    assert "SELECT" in sql
    assert params == (5,)
    assert result == current


def test_deletar_fidelidade_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    fidelidade_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM FIDELIDADE" in sql
    assert "WHERE id_fidelidade = %s" in sql
    assert params == (8,)
    assert cursor.closed is True


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(fidelidade_repository)

    assert "HTTPException" not in source
