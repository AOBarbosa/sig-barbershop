import pytest
from fastapi import HTTPException

from app.schemas.telefone_schema import TelefoneCreate, TelefoneUpdate
from app.services import telefone_service


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


def tel_row(tel_id=1):
    return {"id_telefone": tel_id, "PESSOA_id_pessoa": 1, "numero": "84999999999"}


def test_buscar_telefone_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: tel_row()
    )

    assert telefone_service.buscar_telefone(conn, 1) == tel_row()
    assert conn.started is False


def test_buscar_telefone_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        telefone_service.buscar_telefone(conn, 404)

    assert exc.value.status_code == 404


def test_listar_por_pessoa_existente_retorna_lista(monkeypatch):
    conn = FakeConn()
    rows = [tel_row()]
    monkeypatch.setattr(
        telefone_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        telefone_service.telefone_repository, "listar_por_pessoa", lambda _c, _i: rows
    )

    assert telefone_service.listar_por_pessoa(conn, 1) == rows


def test_listar_por_pessoa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(telefone_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        telefone_service.listar_por_pessoa(conn, 404)

    assert exc.value.status_code == 404


def test_criar_telefone_controla_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        telefone_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        telefone_service.telefone_repository, "criar", lambda _c, _d: tel_row()
    )

    result = telefone_service.criar_telefone(
        conn, TelefoneCreate(PESSOA_id_pessoa=1, numero="84999999999")
    )

    assert result == tel_row()
    assert conn.committed is True


def test_criar_telefone_sem_pessoa_retorna_404_e_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(telefone_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        telefone_service.criar_telefone(
            conn, TelefoneCreate(PESSOA_id_pessoa=999, numero="84999999999")
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_criar_telefone_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        telefone_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )

    def fake(_c, _d):
        raise RuntimeError("erro")

    monkeypatch.setattr(telefone_service.telefone_repository, "criar", fake)

    with pytest.raises(RuntimeError):
        telefone_service.criar_telefone(
            conn, TelefoneCreate(PESSOA_id_pessoa=1, numero="84999999999")
        )

    assert conn.rolled_back is True


def test_atualizar_telefone_existente_controla_transacao(monkeypatch):
    conn = FakeConn()
    novo = tel_row() | {"numero": "84988888888"}
    monkeypatch.setattr(
        telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: tel_row()
    )
    monkeypatch.setattr(
        telefone_service.telefone_repository, "atualizar", lambda _c, _i, _d: novo
    )

    result = telefone_service.atualizar_telefone(
        conn, 1, TelefoneUpdate(numero="84988888888")
    )

    assert result == novo
    assert conn.committed is True


def test_atualizar_telefone_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        telefone_service.atualizar_telefone(conn, 404, TelefoneUpdate(numero="84988888888"))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_telefone_existente_controla_transacao(monkeypatch):
    conn = FakeConn()
    called = []
    monkeypatch.setattr(
        telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: tel_row()
    )
    monkeypatch.setattr(
        telefone_service.telefone_repository, "deletar", lambda _c, i: called.append(i)
    )

    telefone_service.deletar_telefone(conn, 1)

    assert called == [1]
    assert conn.committed is True


def test_deletar_telefone_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(telefone_service.telefone_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        telefone_service.deletar_telefone(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
