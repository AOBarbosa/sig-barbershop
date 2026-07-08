from decimal import Decimal

from app.repositories import venda_produto_repository


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
        "VENDA_id_venda": 1,
        "PRODUTO_id_produto": 2,
        "quantidade": 3,
        "preco_unitario": Decimal("10.00"),
    }


def test_listar_por_venda_consulta_vinculos_da_venda():
    rows = [vinculo_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = venda_produto_repository.listar_por_venda(conn, 1)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM VENDA_PRODUTO" in sql
    assert "WHERE VENDA_id_venda = %s" in sql
    assert params == (1,)
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_vinculo_por_chave_composta():
    cursor = FakeCursor(row=vinculo_row())
    conn = FakeConn(cursor)

    result = venda_produto_repository.buscar_por_id(conn, (1, 2))

    sql, params = cursor.statements[0]
    assert "VENDA_id_venda = %s" in sql
    assert "PRODUTO_id_produto = %s" in sql
    assert params == (1, 2)
    assert result["PRODUTO_id_produto"] == 2


def test_buscar_por_ids_consulta_vinculo_por_venda_e_produto():
    cursor = FakeCursor(row=vinculo_row())
    conn = FakeConn(cursor)

    result = venda_produto_repository.buscar_por_ids(conn, 1, 2)

    sql, params = cursor.statements[0]
    assert "WHERE VENDA_id_venda = %s" in sql
    assert "AND PRODUTO_id_produto = %s" in sql
    assert params == (1, 2)
    assert result == vinculo_row()


def test_criar_insere_vinculo_com_preco_unitario_vigente():
    created = vinculo_row()
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = venda_produto_repository.criar(conn, 1, 2, 3, Decimal("10.00"))

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO VENDA_PRODUTO" in insert_sql
    assert insert_params == (1, 2, 3, Decimal("10.00"))
    assert select_params == (1, 2)
    assert result == created


def test_deletar_por_ids_remove_vinculo():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    venda_produto_repository.deletar_por_ids(conn, 1, 2)

    sql, params = cursor.statements[0]
    assert "DELETE FROM VENDA_PRODUTO" in sql
    assert "WHERE VENDA_id_venda = %s" in sql
    assert "AND PRODUTO_id_produto = %s" in sql
    assert params == (1, 2)
    assert cursor.closed is True
