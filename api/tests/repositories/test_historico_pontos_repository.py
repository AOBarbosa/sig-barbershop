from datetime import datetime
import inspect

from app.repositories import historico_pontos_repository


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


def historico_row(historico_id=1, tipo_movimentacao="ACUMULA"):
    return {
        "id_movimentacao": historico_id,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "VENDA_id_venda": 2,
        "FIDELIDADE_id_fidelidade": 3,
        "pontos": 10,
        "tipo_movimentacao": tipo_movimentacao,
        "data_movimentacao": datetime(2026, 7, 5, 9, 0),
    }


def test_listar_por_cliente_consulta_historico_do_cliente():
    rows = [historico_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = historico_pontos_repository.listar_por_cliente(conn, 1)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM HISTORICO_PONTOS" in sql
    assert "WHERE CLIENTE_PESSOA_id_pessoa = %s" in sql
    assert params == (1,)
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_por_id():
    cursor = FakeCursor(row=historico_row(historico_id=3))
    conn = FakeConn(cursor)

    result = historico_pontos_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "WHERE id_movimentacao = %s" in sql
    assert params == (3,)
    assert result["id_movimentacao"] == 3


def test_criar_insere_movimentacao_de_acumulo():
    created = historico_row(historico_id=10)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = historico_pontos_repository.criar(conn, 1, 2, 3, 10, "ACUMULA")

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO HISTORICO_PONTOS" in insert_sql
    assert "VENDA_id_venda" in insert_sql
    assert "FIDELIDADE_id_fidelidade" in insert_sql
    assert "data_movimentacao" in insert_sql
    assert insert_params == (1, 2, 3, 10, "ACUMULA")
    assert select_params == (10,)
    assert "FROM HISTORICO_PONTOS" in select_sql
    assert result == created


def test_calcular_saldo_soma_acumulo_e_subtrai_resgate():
    cursor = FakeCursor(row={"saldo": 25})
    conn = FakeConn(cursor)

    result = historico_pontos_repository.calcular_saldo(conn, 1)

    sql, params = cursor.statements[0]
    assert "FROM HISTORICO_PONTOS" in sql
    assert "SUM(CASE WHEN tipo_movimentacao = 'ACUMULA' THEN pontos ELSE -pontos END)" in sql
    assert params == (1,)
    assert result == 25


def test_historico_pontos_repository_nao_lanca_http_exception():
    source = inspect.getsource(historico_pontos_repository)

    assert "HTTPException" not in source
