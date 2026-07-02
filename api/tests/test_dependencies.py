from app import dependencies


class FakeConn:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_entrega_conexao_e_fecha_no_finally(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(dependencies, "get_connection", lambda: conn)

    generator = dependencies.get_db()
    yielded = next(generator)

    assert yielded is conn

    try:
        next(generator)
    except StopIteration:
        pass

    assert conn.closed is True
