from app import database


class FakePool:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.connections = []

    def get_connection(self):
        conn = object()
        self.connections.append(conn)
        return conn


def test_get_connection_cria_pool_lazy_com_variaveis_de_ambiente(monkeypatch):
    created_pools = []

    def fake_pool(**kwargs):
        pool = FakePool(**kwargs)
        created_pools.append(pool)
        return pool

    monkeypatch.setattr(database, "_pool", None)
    monkeypatch.setattr(database, "MySQLConnectionPool", fake_pool)
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_NAME", "sig_test")
    monkeypatch.setenv("DB_USER", "barber")
    monkeypatch.setenv("DB_PASSWORD", "secret")

    conn = database.get_connection()

    assert conn is created_pools[0].connections[0]
    assert created_pools[0].kwargs == {
        "pool_name": "barbershop",
        "pool_size": 5,
        "host": "db",
        "port": 3307,
        "database": "sig_test",
        "user": "barber",
        "password": "secret",
        "autocommit": True,
    }


def test_get_connection_reutiliza_pool_existente(monkeypatch):
    pool = FakePool()
    monkeypatch.setattr(database, "_pool", pool)

    conn = database.get_connection()

    assert conn is pool.connections[0]
