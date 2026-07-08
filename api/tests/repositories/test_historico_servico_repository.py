from decimal import Decimal
import inspect

from app.repositories import historico_servico_repository


class FakeCursor:
    def __init__(self, rows=None, row=None):
        self.rows = rows or []
        self.row = row
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


def test_criar_historico_servico_insere_valores_relacionais():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    historico_servico_repository.criar(
        conn,
        servico_id=7,
        preco=Decimal("45.00"),
        duracao_em_minutos=30,
        pontos_gerados=4,
        data_inicio="2026-07-01",
        ativo=False,
    )

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "INSERT INTO HISTORICO_SERVICO" in sql
    assert "SERVICO_id_servico" in sql
    assert "preco" in sql
    assert "duracao_em_minutos" in sql
    assert "pontos_gerados" in sql
    assert "data_inicio" in sql
    assert "ativo" in sql
    assert params == (7, Decimal("45.00"), 30, 4, "2026-07-01", None, False)
    assert cursor.closed is True


def test_listar_por_servico_consulta_historico_ordenado_por_data():
    rows = [
        {
            "id_historico": 1,
            "SERVICO_id_servico": 7,
            "preco": Decimal("45.00"),
            "duracao_em_minutos": 30,
            "pontos_gerados": 4,
            "data_inicio": "2026-07-01",
            "data_fim": None,
            "ativo": 1,
        }
    ]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = historico_servico_repository.listar_por_servico(conn, 7)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM HISTORICO_SERVICO" in sql
    assert "WHERE SERVICO_id_servico = %s" in sql
    assert "ORDER BY data_inicio DESC" in sql
    assert params == (7,)
    assert result == rows
    assert cursor.closed is True


def test_buscar_vigente_filtra_ativo_sem_data_fim():
    row = {"id_historico": 1, "preco": Decimal("45.00")}
    cursor = FakeCursor(row=row)
    conn = FakeConn(cursor)

    result = historico_servico_repository.buscar_vigente(conn, 7)

    sql, params = cursor.statements[0]
    assert "ativo = TRUE" in sql
    assert "data_fim IS NULL" in sql
    assert params == (7,)
    assert result == row


def test_encerrar_vigente_atualiza_historico_ativo_sem_data_fim():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    historico_servico_repository.encerrar_vigente(conn, 7)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "UPDATE HISTORICO_SERVICO" in sql
    assert "data_fim = CURRENT_DATE" in sql
    assert "ativo = FALSE" in sql
    assert "SERVICO_id_servico = %s" in sql
    assert params == (7,)
    assert cursor.closed is True


def test_historico_servico_repository_nao_lanca_http_exception():
    source = inspect.getsource(historico_servico_repository)

    assert "HTTPException" not in source
