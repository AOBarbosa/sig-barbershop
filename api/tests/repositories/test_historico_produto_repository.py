from decimal import Decimal
import inspect

from app.repositories import historico_produto_repository


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


def test_criar_historico_produto_insere_precos_estoques_e_ativo():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    historico_produto_repository.criar(
        conn,
        produto_id=7,
        preco_anterior=Decimal("35.00"),
        preco_novo=Decimal("45.00"),
        estoque_anterior=20,
        estoque_novo=15,
        ativo=False,
    )

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "INSERT INTO HISTORICO_PRODUTO" in sql
    assert "PRODUTO_id_produto" in sql
    assert "preco_anterior" in sql
    assert "preco_novo" in sql
    assert "estoque_anterior" in sql
    assert "estoque_novo" in sql
    assert "ativo" in sql
    assert params == (7, Decimal("35.00"), Decimal("45.00"), 20, 15, False)
    assert cursor.closed is True


def test_listar_por_produto_consulta_historico_ordenado_por_data():
    rows = [
        {
            "id_historico": 1,
            "PRODUTO_id_produto": 7,
            "preco_anterior": Decimal("35.00"),
            "preco_novo": Decimal("45.00"),
            "estoque_anterior": 20,
            "estoque_novo": 15,
            "ativo": 1,
            "alterado_em": "2026-07-02T10:00:00",
        }
    ]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = historico_produto_repository.listar_por_produto(conn, 7)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM HISTORICO_PRODUTO" in sql
    assert "WHERE PRODUTO_id_produto = %s" in sql
    assert "ORDER BY alterado_em DESC" in sql
    assert params == (7,)
    assert result == rows
    assert cursor.closed is True


def test_historico_produto_repository_nao_lanca_http_exception():
    source = inspect.getsource(historico_produto_repository)

    assert "HTTPException" not in source
