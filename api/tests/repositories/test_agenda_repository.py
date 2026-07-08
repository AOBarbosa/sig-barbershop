import inspect

from app.repositories import agenda_repository


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.statements = []
        self.closed = False

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

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


def test_barbeiro_ocupado_no_horario_consulta_sem_atendimento_atual():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = agenda_repository.barbeiro_ocupado_no_horario(conn, 2, "2026-07-13 08:00:00")

    sql, params = cursor.statements[0]
    assert "FROM ATENDIMENTO" in sql
    assert "status <> 'CANCELADO'" in sql
    assert "id_atendimento <>" not in sql
    assert params == (2, "2026-07-13 08:00:00")
    assert result is True


def test_barbeiro_ocupado_no_horario_ignora_atendimento_atual():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = agenda_repository.barbeiro_ocupado_no_horario(
        conn,
        2,
        "2026-07-13 08:00:00",
        atendimento_id=10,
    )

    sql, params = cursor.statements[0]
    assert "id_atendimento <> %s" in sql
    assert params == (2, "2026-07-13 08:00:00", 10)
    assert result is False


def test_listar_horarios_ocupados_barbeiro_retorna_datas_do_intervalo():
    rows = [
        {"data_hora_inicio": "2026-07-13T14:30:00"},
        {"data_hora_inicio": "2026-07-13T15:00:00"},
    ]
    cursor = FakeCursor(row=None)
    cursor.fetchall = lambda: rows
    conn = FakeConn(cursor)

    result = agenda_repository.listar_horarios_ocupados_barbeiro(
        conn,
        2,
        "2026-07-13T00:00:00",
        "2026-07-27T23:59:59",
    )

    sql, params = cursor.statements[0]
    assert "data_hora_inicio >= %s" in sql
    assert "data_hora_inicio <= %s" in sql
    assert "status <> 'CANCELADO'" in sql
    assert params == (2, "2026-07-13T00:00:00", "2026-07-27T23:59:59")
    assert result == rows


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(agenda_repository)
    assert "HTTPException" not in source
