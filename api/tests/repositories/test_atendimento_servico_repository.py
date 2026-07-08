from decimal import Decimal
import inspect

from app.repositories import atendimento_servico_repository


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


def vinculo_row():
    return {
        "ATENDIMENTO_id_atendimento": 1,
        "SERVICO_id_servico": 2,
        "preco_cobrado": Decimal("35.00"),
    }


def test_listar_por_atendimento_usa_cursor_dictionary_e_filtra_por_atendimento():
    rows = [vinculo_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = atendimento_servico_repository.listar_por_atendimento(conn, 1)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM ATENDIMENTO_SERVICO" in sql
    assert "WHERE ATENDIMENTO_id_atendimento = %s" in sql
    assert params == (1,)
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_ids_consulta_vinculo_por_atendimento_e_servico():
    cursor = FakeCursor(row=vinculo_row())
    conn = FakeConn(cursor)

    result = atendimento_servico_repository.buscar_por_ids(conn, 1, 2)

    sql, params = cursor.statements[0]
    assert "FROM ATENDIMENTO_SERVICO" in sql
    assert "ATENDIMENTO_id_atendimento = %s" in sql
    assert "SERVICO_id_servico = %s" in sql
    assert params == (1, 2)
    assert result == vinculo_row()


def test_criar_vinculo_insere_preco_cobrado_e_retorna_registro():
    created = vinculo_row()
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = atendimento_servico_repository.criar(
        conn,
        atendimento_id=1,
        servico_id=2,
        preco_cobrado=Decimal("35.00"),
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO ATENDIMENTO_SERVICO" in insert_sql
    assert insert_params == (1, 2, Decimal("35.00"))
    assert "FROM ATENDIMENTO_SERVICO" in select_sql
    assert select_params == (1, 2)
    assert result == created


def test_buscar_por_id_consulta_vinculo_por_chave_composta():
    cursor = FakeCursor(row=vinculo_row())
    conn = FakeConn(cursor)

    result = atendimento_servico_repository.buscar_por_id(conn, (1, 2))

    sql, params = cursor.statements[0]
    assert "ATENDIMENTO_id_atendimento = %s" in sql
    assert "SERVICO_id_servico = %s" in sql
    assert params == (1, 2)
    assert result["SERVICO_id_servico"] == 2


def test_deletar_por_ids_remove_vinculo_por_atendimento_e_servico():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    atendimento_servico_repository.deletar_por_ids(conn, 1, 2)

    sql, params = cursor.statements[0]
    assert "DELETE FROM ATENDIMENTO_SERVICO" in sql
    assert "ATENDIMENTO_id_atendimento = %s" in sql
    assert "SERVICO_id_servico = %s" in sql
    assert params == (1, 2)
    assert cursor.closed is True


def test_atendimento_servico_repository_nao_lanca_http_exception():
    source = inspect.getsource(atendimento_servico_repository)

    assert "HTTPException" not in source
