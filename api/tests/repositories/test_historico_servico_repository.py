from decimal import Decimal
import inspect

from app.repositories import historico_servico_repository


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.statements = []
        self.closed = False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConn:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.cursor_kwargs = None

    def cursor(self, **kwargs):
        self.cursor_kwargs = kwargs
        return self.fake_cursor


def test_criar_historico_servico_insere_preco_anterior_preco_novo_e_ativo():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    historico_servico_repository.criar(
        conn,
        servico_id=7,
        preco_anterior=Decimal("35.00"),
        preco_novo=Decimal("45.00"),
        ativo=False,
    )

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "INSERT INTO HISTORICO_SERVICO" in sql
    assert "SERVICO_id_servico" in sql
    assert "preco_anterior" in sql
    assert "preco_novo" in sql
    assert "ativo" in sql
    assert params == (7, Decimal("35.00"), Decimal("45.00"), False)
    assert cursor.closed is True


def test_listar_por_servico_consulta_historico_ordenado_por_data():
    rows = [
        {
            "id_historico": 1,
            "SERVICO_id_servico": 7,
            "preco_anterior": Decimal("35.00"),
            "preco_novo": Decimal("45.00"),
            "ativo": 1,
            "alterado_em": "2026-07-02T10:00:00",
        }
    ]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = historico_servico_repository.listar_por_servico(conn, 7)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM HISTORICO_SERVICO" in sql
    assert "WHERE SERVICO_id_servico = %s" in sql
    assert "ORDER BY alterado_em DESC" in sql
    assert params == (7,)
    assert result == rows
    assert cursor.closed is True


def test_historico_servico_repository_nao_lanca_http_exception():
    source = inspect.getsource(historico_servico_repository)

    assert "HTTPException" not in source
