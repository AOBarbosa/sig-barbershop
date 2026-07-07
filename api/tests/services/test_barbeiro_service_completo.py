from datetime import date, datetime

import pytest
from fastapi import HTTPException

from app.schemas.barbeiro_schema import BarbeiroCompletoCreate
from app.services import barbeiro_service


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
        "nome": "Pedro",
        "cpf": "55566677788",
        "email": "p@ex.com",
        "data_nascimento": date(1988, 11, 3),
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def _barbeiro_row(barb_id=1, pessoa_id=1):
    return {
        "id_barbeiro": barb_id,
        "PESSOA_id_pessoa": pessoa_id,
        "especialidade": "Corte",
        "ativo": True,
    }


def _payload(cpf="55566677788", email="p@ex.com"):
    return BarbeiroCompletoCreate(
        nome="Pedro",
        cpf=cpf,
        email=email,
        data_nascimento=date(1988, 11, 3),
        especialidade="Corte",
        ativo=True,
    )


def test_criar_barbeiro_completo_cria_pessoa_e_barbeiro_em_transacao(monkeypatch):
    conn = FakeConn()
    pessoa = _pessoa_row()
    barbeiro = _barbeiro_row(pessoa_id=pessoa["id_pessoa"])

    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "criar", lambda _c, _d: pessoa
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "criar", lambda _c, _d: barbeiro
    )

    result = barbeiro_service.criar_barbeiro_completo(conn, _payload())

    assert result == {"barbeiro": barbeiro, "pessoa": pessoa}
    assert conn.committed is True


def test_criar_barbeiro_completo_cpf_duplicado_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_cpf",
        lambda _c, _v: _pessoa_row(),
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.criar_barbeiro_completo(conn, _payload())

    assert exc.value.status_code == 409
    assert "CPF" in exc.value.detail
    assert conn.rolled_back is True


def test_criar_barbeiro_completo_email_duplicado_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_email",
        lambda _c, _v: _pessoa_row(),
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.criar_barbeiro_completo(conn, _payload())

    assert exc.value.status_code == 409
    assert "Email" in exc.value.detail
    assert conn.rolled_back is True


def test_criar_barbeiro_completo_sem_email_nao_verifica_duplicidade(monkeypatch):
    conn = FakeConn()
    chamou_email = False

    def fake_email(_c, _v):
        nonlocal chamou_email
        chamou_email = True
        return None

    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", fake_email
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "criar", lambda _c, _d: _pessoa_row()
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "criar", lambda _c, _d: _barbeiro_row()
    )

    barbeiro_service.criar_barbeiro_completo(
        conn,
        BarbeiroCompletoCreate(
            nome="X", cpf="00000000000", email=None, especialidade="Corte", ativo=True
        ),
    )

    assert chamou_email is False
    assert conn.committed is True


def test_criar_barbeiro_completo_falha_ao_criar_barbeiro_reverte_pessoa(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "criar", lambda _c, _d: _pessoa_row()
    )

    def fake_criar_barbeiro(_c, _d):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "criar", fake_criar_barbeiro
    )

    with pytest.raises(RuntimeError):
        barbeiro_service.criar_barbeiro_completo(conn, _payload())

    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_barbeiro_completo_passa_dados_profissionais_corretos(monkeypatch):
    conn = FakeConn()
    dados_capturados = {}
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "criar", lambda _c, _d: _pessoa_row()
    )

    def fake_criar(_c, d):
        dados_capturados.update(d)
        return _barbeiro_row()

    monkeypatch.setattr(barbeiro_service.barbeiro_repository, "criar", fake_criar)

    payload = BarbeiroCompletoCreate(
        nome="Rafael",
        cpf="66677788899",
        email=None,
        data_nascimento=None,
        especialidade="Barba",
        ativo=False,
    )
    barbeiro_service.criar_barbeiro_completo(conn, payload)

    assert dados_capturados["especialidade"] == "Barba"
    assert dados_capturados["ativo"] is False
    assert "PESSOA_id_pessoa" in dados_capturados
