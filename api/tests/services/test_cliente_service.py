import pytest
from fastapi import HTTPException

from app.schemas.cliente_schema import ClienteCreate
from app.services import cliente_service


class FakeConn:
    def __init__(self):
        self.started = False
        self.committed = False
        self.rolled_back = False

    def start_transaction(self):
        self.started = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def cli_row(cli_id=1, pessoa_id=1):
    return {"id_cliente": cli_id, "PESSOA_id_pessoa": pessoa_id}


def test_listar_clientes_sem_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(cliente_service.cliente_repository, "listar", lambda _c: [cli_row()])

    assert cliente_service.listar_clientes(conn) == [cli_row()]
    assert conn.started is False


def test_buscar_cliente_existente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_id", lambda _c, _i: cli_row()
    )

    assert cliente_service.buscar_cliente(conn, 1) == cli_row()


def test_buscar_cliente_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(cliente_service.cliente_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        cliente_service.buscar_cliente(conn, 404)

    assert exc.value.status_code == 404


def test_criar_cliente_controla_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: None
    )
    monkeypatch.setattr(cliente_service.cliente_repository, "criar", lambda _c, _d: cli_row())

    result = cliente_service.criar_cliente(conn, ClienteCreate(PESSOA_id_pessoa=1))

    assert result == cli_row()
    assert conn.committed is True


def test_criar_cliente_sem_pessoa_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(cliente_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        cliente_service.criar_cliente(conn, ClienteCreate(PESSOA_id_pessoa=999))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_criar_cliente_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: cli_row()
    )

    with pytest.raises(HTTPException) as exc:
        cliente_service.criar_cliente(conn, ClienteCreate(PESSOA_id_pessoa=1))

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_criar_cliente_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: None
    )

    def fake(_c, _d):
        raise RuntimeError("erro")

    monkeypatch.setattr(cliente_service.cliente_repository, "criar", fake)

    with pytest.raises(RuntimeError):
        cliente_service.criar_cliente(conn, ClienteCreate(PESSOA_id_pessoa=1))

    assert conn.rolled_back is True


def test_deletar_cliente_sem_vinculo_controla_transacao(monkeypatch):
    conn = FakeConn()
    called = []
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_id", lambda _c, _i: cli_row()
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "existe_vinculo", lambda _c, _i: False
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "deletar", lambda _c, i: called.append(i)
    )

    cliente_service.deletar_cliente(conn, 1)

    assert called == [1]
    assert conn.committed is True


def test_deletar_cliente_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(cliente_service.cliente_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        cliente_service.deletar_cliente(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_cliente_com_vinculo_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.cliente_repository, "buscar_por_id", lambda _c, _i: cli_row()
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "existe_vinculo", lambda _c, _i: True
    )

    with pytest.raises(HTTPException) as exc:
        cliente_service.deletar_cliente(conn, 1)

    assert exc.value.status_code == 409
    assert conn.rolled_back is True
