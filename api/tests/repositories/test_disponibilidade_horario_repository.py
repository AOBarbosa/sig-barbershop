from app.repositories import disponibilidade_repository


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.statements = []

    def execute(self, sql, params=None):
        self.statements.append((sql, params))

    def fetchone(self):
        return self.row

    def close(self):
        pass


class FakeConn:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    def cursor(self, **_kwargs):
        return self.fake_cursor


def test_barbeiro_disponivel_no_horario_retorna_true_quando_encontra_intervalo():
    cursor = FakeCursor(row={"total": 1})
    conn = FakeConn(cursor)

    result = disponibilidade_repository.barbeiro_disponivel_no_horario(
        conn,
        2,
        "2026-07-13 08:00:00",
    )

    sql, params = cursor.statements[0]
    assert "FROM DISPONIBILIDADE" in sql
    assert "DAYOFWEEK" in sql
    assert params == (2, "2026-07-13 08:00:00", "2026-07-13 08:00:00", "2026-07-13 08:00:00")
    assert result is True


def test_barbeiro_disponivel_no_horario_retorna_false_sem_intervalo():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = disponibilidade_repository.barbeiro_disponivel_no_horario(
        conn,
        2,
        "2026-07-14 08:00:00",
    )

    assert result is False
