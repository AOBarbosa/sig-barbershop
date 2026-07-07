from datetime import date, datetime

import pytest
from fastapi import HTTPException

from app.schemas.cliente_schema import ClienteCompletoCreate
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


def _pessoa_row(pessoa_id=1):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": "12345678901",
        "email": "f@ex.com",
        "data_nascimento": date(1990, 1, 1),
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def _cliente_row(cli_id=1, pessoa_id=1):
    return {"id_cliente": cli_id, "PESSOA_id_pessoa": pessoa_id}


def _payload(cpf="12345678901", email="f@ex.com"):
    return ClienteCompletoCreate(
        nome="Fulano",
        cpf=cpf,
        email=email,
        data_nascimento=date(1990, 1, 1),
    )


def test_criar_cliente_completo_cria_pessoa_e_cliente_em_transacao(monkeypatch):
    conn = FakeConn()
    pessoa = _pessoa_row()
    cliente = _cliente_row(pessoa_id=pessoa["id_pessoa"])

    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "criar", lambda _c, _d: pessoa
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "criar", lambda _c, _d: cliente
    )

    result = cliente_service.criar_cliente_completo(conn, _payload())

    assert result == {"cliente": cliente, "pessoa": pessoa}
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_cliente_completo_cpf_duplicado_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository,
        "buscar_por_cpf",
        lambda _c, _v: _pessoa_row(),
    )

    with pytest.raises(HTTPException) as exc:
        cliente_service.criar_cliente_completo(conn, _payload())

    assert exc.value.status_code == 409
    assert "CPF" in exc.value.detail
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_cliente_completo_email_duplicado_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository,
        "buscar_por_email",
        lambda _c, _v: _pessoa_row(),
    )

    with pytest.raises(HTTPException) as exc:
        cliente_service.criar_cliente_completo(conn, _payload())

    assert exc.value.status_code == 409
    assert "Email" in exc.value.detail
    assert conn.rolled_back is True


def test_criar_cliente_completo_sem_email_nao_verifica_duplicidade(monkeypatch):
    conn = FakeConn()
    chamou_email = False

    def fake_email(_c, _v):
        nonlocal chamou_email
        chamou_email = True
        return None

    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_email", fake_email
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "criar", lambda _c, _d: _pessoa_row()
    )
    monkeypatch.setattr(
        cliente_service.cliente_repository, "criar", lambda _c, _d: _cliente_row()
    )

    cliente_service.criar_cliente_completo(
        conn,
        ClienteCompletoCreate(nome="X", cpf="99999999999", email=None),
    )

    assert chamou_email is False
    assert conn.committed is True


def test_criar_cliente_completo_falha_ao_criar_cliente_reverte_pessoa(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "criar", lambda _c, _d: _pessoa_row()
    )

    def fake_criar_cliente(_c, _d):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(cliente_service.cliente_repository, "criar", fake_criar_cliente)

    with pytest.raises(RuntimeError):
        cliente_service.criar_cliente_completo(conn, _payload())

    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_cliente_completo_falha_ao_criar_pessoa_reverte(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        cliente_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )

    def fake_criar_pessoa(_c, _d):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(cliente_service.pessoa_repository, "criar", fake_criar_pessoa)

    with pytest.raises(RuntimeError):
        cliente_service.criar_cliente_completo(conn, _payload())

    assert conn.rolled_back is True
    assert conn.committed is False
