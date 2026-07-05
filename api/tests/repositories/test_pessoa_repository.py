from datetime import date, datetime
import inspect

from app.repositories import pessoa_repository


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


def pessoa_row(pessoa_id=1):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": "12345678901",
        "email": "f@ex.com",
        "data_nascimento": date(1990, 1, 1),
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def test_listar_pessoas_usa_cursor_dictionary_e_retorna_linhas():
    rows = [pessoa_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = pessoa_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM PESSOA" in cursor.statements[0][0]
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_pessoa_por_id():
    cursor = FakeCursor(row=pessoa_row(pessoa_id=3))
    conn = FakeConn(cursor)

    result = pessoa_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert "FROM PESSOA" in sql
    assert "WHERE id_pessoa = %s" in sql
    assert params == (3,)
    assert result["id_pessoa"] == 3


def test_buscar_por_cpf_consulta_pessoa_por_cpf():
    cursor = FakeCursor(row=pessoa_row())
    conn = FakeConn(cursor)

    result = pessoa_repository.buscar_por_cpf(conn, "12345678901")

    sql, params = cursor.statements[0]
    assert "WHERE cpf = %s" in sql
    assert params == ("12345678901",)
    assert result is not None


def test_buscar_por_email_consulta_pessoa_por_email():
    cursor = FakeCursor(row=pessoa_row())
    conn = FakeConn(cursor)

    result = pessoa_repository.buscar_por_email(conn, "f@ex.com")

    sql, params = cursor.statements[0]
    assert "WHERE email = %s" in sql
    assert params == ("f@ex.com",)
    assert result is not None


def test_criar_pessoa_insere_sql_puro_e_retorna_registro_criado():
    created = pessoa_row(pessoa_id=10) | {"nome": "Novo"}
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = pessoa_repository.criar(
        conn,
        {
            "nome": "Novo",
            "cpf": "99999999999",
            "email": "n@ex.com",
            "data_nascimento": date(1985, 5, 20),
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO PESSOA" in insert_sql
    assert insert_params == ("Novo", "99999999999", "n@ex.com", date(1985, 5, 20))
    assert "FROM PESSOA" in select_sql
    assert select_params == (10,)
    assert result == created


def test_criar_pessoa_aceita_email_e_data_nulos():
    created = pessoa_row(pessoa_id=11)
    cursor = FakeCursor(row=created, lastrowid=11)
    conn = FakeConn(cursor)

    pessoa_repository.criar(conn, {"nome": "X", "cpf": "11111111111"})

    _, insert_params = cursor.statements[0]
    assert insert_params == ("X", "11111111111", None, None)


def test_atualizar_pessoa_executa_update_apenas_dos_campos_recebidos():
    updated = pessoa_row(pessoa_id=4) | {"nome": "Alterado"}
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = pessoa_repository.atualizar(conn, 4, {"nome": "Alterado"})

    update_sql, update_params = cursor.statements[0]
    assert "UPDATE PESSOA" in update_sql
    assert "nome = %s" in update_sql
    assert "cpf = %s" not in update_sql
    assert update_params == ("Alterado", 4)
    assert result == updated


def test_atualizar_pessoa_sem_campos_nao_executa_update():
    current = pessoa_row(pessoa_id=5)
    cursor = FakeCursor(row=current)
    conn = FakeConn(cursor)

    result = pessoa_repository.atualizar(conn, 5, {})

    assert len(cursor.statements) == 1
    sql, _ = cursor.statements[0]
    assert "SELECT" in sql
    assert result == current


def test_deletar_pessoa_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    pessoa_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM PESSOA" in sql
    assert "WHERE id_pessoa = %s" in sql
    assert params == (8,)


def test_existe_vinculo_retorna_true_quando_soma_positiva():
    cursor = FakeCursor(row={"clientes": 0, "barbeiros": 1, "caixas": 0})
    conn = FakeConn(cursor)

    result = pessoa_repository.existe_vinculo(conn, 7)

    sql, params = cursor.statements[0]
    assert "FROM CLIENTE" in sql
    assert "FROM BARBEIRO" in sql
    assert "FROM CAIXA" in sql
    assert params == (7, 7, 7)
    assert result is True


def test_existe_vinculo_retorna_false_quando_soma_zero():
    cursor = FakeCursor(row={"clientes": 0, "barbeiros": 0, "caixas": 0})
    conn = FakeConn(cursor)

    assert pessoa_repository.existe_vinculo(conn, 7) is False


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(pessoa_repository)
    assert "HTTPException" not in source
