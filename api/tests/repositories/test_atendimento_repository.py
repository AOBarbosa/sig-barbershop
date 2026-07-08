from datetime import datetime
from decimal import Decimal
import inspect

from app.repositories import atendimento_repository


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


def atendimento_row(atendimento_id=1):
    return {
        "id_atendimento": atendimento_id,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "BARBEIRO_PESSOA_id_pessoa": 2,
        "data_hora_inicio": datetime(2026, 7, 5, 9, 0),
        "status": "AGENDADO",
        "valor_total": Decimal("0.00"),
        "observacoes": "Primeiro atendimento",
    }


def test_listar_atendimentos_usa_cursor_dictionary_e_retorna_linhas():
    rows = [atendimento_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = atendimento_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM ATENDIMENTO" in cursor.statements[0][0]
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_atendimento_por_id():
    cursor = FakeCursor(row=atendimento_row(atendimento_id=3))
    conn = FakeConn(cursor)

    result = atendimento_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM ATENDIMENTO" in sql
    assert "WHERE id_atendimento = %s" in sql
    assert params == (3,)
    assert result["id_atendimento"] == 3
    assert cursor.closed is True


def test_criar_atendimento_insere_sem_receber_valor_total_do_cliente():
    created = atendimento_row(atendimento_id=10)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = atendimento_repository.criar(
        conn,
        {
            "CLIENTE_PESSOA_id_pessoa": 1,
            "BARBEIRO_PESSOA_id_pessoa": 2,
            "data_hora_inicio": datetime(2026, 7, 5, 9, 0),
            "status": "AGENDADO",
            "valor_total": Decimal("0.00"),
            "observacoes": "Primeiro atendimento",
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO ATENDIMENTO" in insert_sql
    assert insert_params == (
        1,
        2,
        datetime(2026, 7, 5, 9, 0),
        None,
        "AGENDADO",
        Decimal("0.00"),
        "Primeiro atendimento",
    )
    assert select_params == (10,)
    assert "FROM ATENDIMENTO" in select_sql
    assert result == created


def test_atualizar_atendimento_executa_update_apenas_campos_recebidos():
    updated = atendimento_row(atendimento_id=4) | {"observacoes": "Remarcado"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = atendimento_repository.atualizar(conn, 4, {"observacoes": "Remarcado"})

    update_sql, update_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "UPDATE ATENDIMENTO" in update_sql
    assert "observacoes = %s" in update_sql
    assert "valor_total = %s" not in update_sql
    assert update_params == ("Remarcado", 4)
    assert "FROM ATENDIMENTO" in select_sql
    assert select_params == (4,)
    assert result == updated


def test_atualizar_atendimento_sem_campos_nao_executa_update():
    current = atendimento_row(atendimento_id=5)
    cursor = FakeCursor(row=current)
    conn = FakeConn(cursor)

    result = atendimento_repository.atualizar(conn, 5, {})

    assert len(cursor.statements) == 1
    assert "SELECT" in cursor.statements[0][0]
    assert cursor.statements[0][1] == (5,)
    assert result == current


def test_atualizar_status_altera_apenas_status():
    updated = atendimento_row(atendimento_id=6) | {"status": "CONCLUIDO"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = atendimento_repository.atualizar_status(conn, 6, "CONCLUIDO")

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE ATENDIMENTO" in update_sql
    assert "status = %s" in update_sql
    assert update_params == ("CONCLUIDO", 6)
    assert result == updated


def test_deletar_atendimento_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    atendimento_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM ATENDIMENTO" in sql
    assert "WHERE id_atendimento = %s" in sql
    assert params == (8,)
    assert cursor.closed is True


def test_cliente_existe_consulta_cliente():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = atendimento_repository.cliente_existe(conn, 1)

    assert "FROM CLIENTE" in cursor.statements[0][0]
    assert cursor.statements[0][1] == (1,)
    assert result is True


def test_cliente_existe_retorna_false_quando_nao_encontra():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = atendimento_repository.cliente_existe(conn, 1)

    assert result is False


def test_barbeiro_existe_consulta_barbeiro():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = atendimento_repository.barbeiro_existe(conn, 2)

    assert "FROM BARBEIRO" in cursor.statements[0][0]
    assert cursor.statements[0][1] == (2,)
    assert result is True


def test_barbeiro_existe_retorna_false_quando_nao_encontra():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = atendimento_repository.barbeiro_existe(conn, 2)

    assert result is False


def test_calcular_valor_total_soma_precos_cobrados_do_atendimento():
    cursor = FakeCursor(row={"valor_total": Decimal("75.00")})
    conn = FakeConn(cursor)

    result = atendimento_repository.calcular_valor_total(conn, 9)

    sql, params = cursor.statements[0]
    assert "FROM ATENDIMENTO_SERVICO" in sql
    assert "SUM(preco_cobrado)" in sql
    assert params == (9,)
    assert result == Decimal("75.00")


def test_atualizar_valor_total_grava_valor_calculado_pelo_service():
    updated = atendimento_row(atendimento_id=7) | {"valor_total": Decimal("75.00")}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = atendimento_repository.atualizar_valor_total(conn, 7, Decimal("75.00"))

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE ATENDIMENTO" in update_sql
    assert "valor_total = %s" in update_sql
    assert update_params == (Decimal("75.00"), 7)
    assert result == updated


def test_atendimento_repository_nao_lanca_http_exception():
    source = inspect.getsource(atendimento_repository)

    assert "HTTPException" not in source
