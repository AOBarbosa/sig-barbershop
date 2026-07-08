from datetime import time
import inspect

from app.repositories import disponibilidade_repository


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


def disp_row(disp_id=1, dia="segunda"):
    return {
        "id_disponibilidade": disp_id,
        "BARBEIRO_PESSOA_id_pessoa": 1,
        "dia_semana": dia,
        "hora_inicio": time(9, 0),
        "hora_fim": time(18, 0),
    }


def test_buscar_por_id():
    cursor = FakeCursor(row=disp_row(3))
    conn = FakeConn(cursor)

    result = disponibilidade_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM DISPONIBILIDADE" in sql
    assert "CAST(hora_inicio AS CHAR)" in sql
    assert "CAST(hora_fim AS CHAR)" in sql
    assert "WHERE id_disponibilidade = %s" in sql
    assert params == (3,)
    assert result["id_disponibilidade"] == 3


def test_listar_por_barbeiro_ordena_por_dia_semana():
    cursor = FakeCursor(rows=[disp_row()])
    conn = FakeConn(cursor)

    result = disponibilidade_repository.listar_por_barbeiro(conn, 1)

    sql, params = cursor.statements[0]
    assert "WHERE BARBEIRO_PESSOA_id_pessoa = %s" in sql
    assert "FIELD(dia_semana" in sql
    assert "SEGUNDA" in sql
    assert "DOMINGO" in sql
    assert params == (1,)
    assert len(result) == 1


def test_buscar_por_barbeiro_e_dia():
    cursor = FakeCursor(row=disp_row(dia="terca"))
    conn = FakeConn(cursor)

    result = disponibilidade_repository.buscar_por_barbeiro_e_dia(conn, 1, "terca")

    sql, params = cursor.statements[0]
    assert "WHERE BARBEIRO_PESSOA_id_pessoa = %s AND dia_semana = %s" in sql
    assert params == (1, "terca")
    assert result["dia_semana"] == "terca"


def test_criar_disponibilidade_insere_e_retorna_registro():
    created = disp_row(10)
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = disponibilidade_repository.criar(
        conn,
        {
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "segunda",
            "hora_inicio": time(9, 0),
            "hora_fim": time(18, 0),
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    assert "INSERT INTO DISPONIBILIDADE" in insert_sql
    assert insert_params == (1, "segunda", time(9, 0), time(18, 0))
    assert result == created


def test_atualizar_disponibilidade_apenas_campos_recebidos():
    updated = disp_row() | {"hora_fim": time(19, 0)}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = disponibilidade_repository.atualizar(conn, 1, {"hora_fim": time(19, 0)})

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE DISPONIBILIDADE" in update_sql
    assert "hora_fim = %s" in update_sql
    assert "hora_inicio = %s" not in update_sql
    assert update_params == (time(19, 0), 1)
    assert result == updated


def test_atualizar_disponibilidade_sem_campos_nao_executa_update():
    cursor = FakeCursor(row=disp_row())
    conn = FakeConn(cursor)

    disponibilidade_repository.atualizar(conn, 1, {})

    assert len(cursor.statements) == 1
    assert "SELECT" in cursor.statements[0][0]


def test_deletar_disponibilidade():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    disponibilidade_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM DISPONIBILIDADE" in sql
    assert params == (8,)


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(disponibilidade_repository)
    assert "HTTPException" not in source
