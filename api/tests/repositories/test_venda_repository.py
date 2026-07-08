from datetime import datetime
from decimal import Decimal
import inspect

from app.repositories import venda_repository


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


def venda_row(venda_id=1):
    return {
        "id_venda": venda_id,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "CAIXA_PESSOA_id_pessoa": 2,
        "data_hora": datetime(2026, 7, 5, 9, 0),
        "valor_total": Decimal("0.00"),
        "status": "ABERTA",
        "forma_pagamento": "PIX",
        "desconto": Decimal("0.00"),
    }


def test_listar_vendas_usa_cursor_dictionary_e_retorna_linhas():
    rows = [venda_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = venda_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM VENDA" in cursor.statements[0][0]
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_venda_por_id():
    cursor = FakeCursor(row=venda_row(venda_id=3))
    conn = FakeConn(cursor)

    result = venda_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM VENDA" in sql
    assert "WHERE id_venda = %s" in sql
    assert params == (3,)
    assert result["id_venda"] == 3
    assert cursor.closed is True


def test_criar_venda_insere_sem_receber_valor_total_do_cliente():
    created = venda_row(venda_id=10)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = venda_repository.criar(
        conn,
        {
            "CLIENTE_PESSOA_id_pessoa": 1,
            "CAIXA_PESSOA_id_pessoa": 2,
            "data_hora": datetime(2026, 7, 5, 9, 0),
            "valor_total": Decimal("0.00"),
            "status": "ABERTA",
            "forma_pagamento": "PIX",
            "desconto": Decimal("0.00"),
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO VENDA" in insert_sql
    assert insert_params == (
        1,
        2,
        datetime(2026, 7, 5, 9, 0),
        Decimal("0.00"),
        "ABERTA",
        "PIX",
        Decimal("0.00"),
    )
    assert select_params == (10,)
    assert "FROM VENDA" in select_sql
    assert result == created


def test_atualizar_status_altera_apenas_status():
    updated = venda_row(venda_id=6) | {"status": "PAGA"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = venda_repository.atualizar_status(conn, 6, "PAGA")

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE VENDA" in update_sql
    assert "status = %s" in update_sql
    assert update_params == ("PAGA", 6)
    assert result == updated


def test_deletar_venda_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    venda_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM VENDA" in sql
    assert "WHERE id_venda = %s" in sql
    assert params == (8,)
    assert cursor.closed is True


def test_cliente_existe_consulta_cliente():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = venda_repository.cliente_existe(conn, 1)

    assert "FROM CLIENTE" in cursor.statements[0][0]
    assert cursor.statements[0][1] == (1,)
    assert result is True


def test_cliente_existe_retorna_false_quando_nao_encontra():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = venda_repository.cliente_existe(conn, 1)

    assert result is False


def test_caixa_existe_consulta_caixa():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = venda_repository.caixa_existe(conn, 2)

    assert "FROM CAIXA" in cursor.statements[0][0]
    assert cursor.statements[0][1] == (2,)
    assert result is True


def test_caixa_existe_retorna_false_quando_nao_encontra():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = venda_repository.caixa_existe(conn, 2)

    assert result is False


def test_calcular_valor_total_soma_quantidade_vezes_preco_unitario_da_venda():
    cursor = FakeCursor(row={"valor_total": Decimal("150.00")})
    conn = FakeConn(cursor)

    result = venda_repository.calcular_valor_total(conn, 9)

    sql, params = cursor.statements[0]
    assert "FROM VENDA_PRODUTO" in sql
    assert "SUM(quantidade * preco_unitario)" in sql
    assert params == (9,)
    assert result == Decimal("150.00")


def test_atualizar_valor_total_grava_valor_calculado_pelo_service():
    updated = venda_row(venda_id=7) | {"valor_total": Decimal("150.00")}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = venda_repository.atualizar_valor_total(conn, 7, Decimal("150.00"))

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE VENDA" in update_sql
    assert "valor_total = %s" in update_sql
    assert update_params == (Decimal("150.00"), 7)
    assert result == updated


def test_venda_repository_nao_lanca_http_exception():
    source = inspect.getsource(venda_repository)

    assert "HTTPException" not in source
