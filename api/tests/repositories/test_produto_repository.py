from decimal import Decimal
import inspect

from app.repositories import produto_repository


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


def produto_row(produto_id=1):
    return {
        "id_produto": produto_id,
        "nome": "Pomada modeladora",
        "descricao": "Pomada efeito matte",
        "preco": Decimal("35.00"),
        "estoque": 20,
        "ativo": 1,
    }


def test_listar_produtos_usa_cursor_dictionary_e_retorna_linhas():
    rows = [produto_row()]
    cursor = FakeCursor(rows=rows)
    conn = FakeConn(cursor)

    result = produto_repository.listar(conn)

    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM PRODUTO" in cursor.statements[0][0]
    assert result == rows
    assert cursor.closed is True


def test_buscar_por_id_consulta_produto_por_id():
    cursor = FakeCursor(row=produto_row(produto_id=3))
    conn = FakeConn(cursor)

    result = produto_repository.buscar_por_id(conn, 3)

    sql, params = cursor.statements[0]
    assert conn.cursor_kwargs == {"dictionary": True}
    assert "FROM PRODUTO" in sql
    assert "WHERE id_produto = %s" in sql
    assert params == (3,)
    assert result["id_produto"] == 3
    assert cursor.closed is True


def test_criar_produto_insere_sql_puro_e_retorna_registro_criado():
    created = produto_row(produto_id=10) | {
        "nome": "Shampoo",
        "descricao": "Shampoo anticaspa",
        "preco": Decimal("25.00"),
        "estoque": 15,
    }
    cursor = FakeCursor(row=created, lastrowid=10)
    conn = FakeConn(cursor)

    result = produto_repository.criar(
        conn,
        {
            "nome": "Shampoo",
            "descricao": "Shampoo anticaspa",
            "preco": Decimal("25.00"),
            "estoque": 15,
            "ativo": True,
        },
    )

    insert_sql, insert_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "INSERT INTO PRODUTO" in insert_sql
    assert insert_params == ("Shampoo", "Shampoo anticaspa", Decimal("25.00"), 15, True)
    assert "FROM PRODUTO" in select_sql
    assert select_params == (10,)
    assert result == created
    assert cursor.closed is True


def test_atualizar_produto_executa_update_apenas_dos_campos_recebidos_e_retorna_registro():
    updated = produto_row(produto_id=4) | {
        "nome": "Pomada premium",
        "preco": Decimal("45.00"),
    }
    cursor = FakeCursor(row=updated)
    conn = FakeConn(cursor)

    result = produto_repository.atualizar(
        conn,
        4,
        {
            "nome": "Pomada premium",
            "preco": Decimal("45.00"),
        },
    )

    update_sql, update_params = cursor.statements[0]
    select_sql, select_params = cursor.statements[1]
    assert "UPDATE PRODUTO" in update_sql
    assert "nome = %s" in update_sql
    assert "preco = %s" in update_sql
    assert "descricao = %s" not in update_sql
    assert update_params == ("Pomada premium", Decimal("45.00"), 4)
    assert "FROM PRODUTO" in select_sql
    assert select_params == (4,)
    assert result == updated


def test_atualizar_produto_sem_campos_nao_executa_update_e_retorna_registro_atual():
    current = produto_row(produto_id=5)
    cursor = FakeCursor(row=current)
    conn = FakeConn(cursor)

    result = produto_repository.atualizar(conn, 5, {})

    assert len(cursor.statements) == 1
    sql, params = cursor.statements[0]
    assert "SELECT" in sql
    assert params == (5,)
    assert result == current


def test_deletar_produto_remove_por_id():
    cursor = FakeCursor()
    conn = FakeConn(cursor)

    produto_repository.deletar(conn, 8)

    sql, params = cursor.statements[0]
    assert "DELETE FROM PRODUTO" in sql
    assert "WHERE id_produto = %s" in sql
    assert params == (8,)
    assert cursor.closed is True


def test_existe_venda_vinculada_consulta_tabela_de_juncao():
    cursor = FakeCursor(row={"total": 2})
    conn = FakeConn(cursor)

    result = produto_repository.existe_venda_vinculada(conn, 7)

    sql, params = cursor.statements[0]
    assert "FROM VENDA_PRODUTO" in sql
    assert params == (7,)
    assert result is True


def test_existe_venda_vinculada_retorna_false_quando_nao_ha_vinculo():
    cursor = FakeCursor(row={"total": 0})
    conn = FakeConn(cursor)

    result = produto_repository.existe_venda_vinculada(conn, 7)

    assert result is False


def test_repository_nao_lanca_http_exception():
    source = inspect.getsource(produto_repository)

    assert "HTTPException" not in source
