from datetime import date, datetime

import pytest
from fastapi import HTTPException

from app.schemas.barbeiro_schema import BarbeiroCompletoCreate, BarbeiroCompletoUpdate
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


def test_atualizar_barbeiro_completo_atualiza_pessoa_e_barbeiro_em_transacao(monkeypatch):
    conn = FakeConn()
    barbeiro_atual = _barbeiro_row(pessoa_id=10)
    pessoa = _pessoa_row(pessoa_id=10) | {"nome": "Pedro Atualizado"}
    barbeiro = barbeiro_atual | {"especialidade": "Barba", "ativo": False}
    pessoa_payload = {}
    barbeiro_payload = {}

    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: barbeiro_atual,
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )

    def fake_atualizar_pessoa(_c, _id, data):
        pessoa_payload.update(data)
        return pessoa

    def fake_atualizar_barbeiro(_c, _id, data):
        barbeiro_payload.update(data)
        return barbeiro

    monkeypatch.setattr(barbeiro_service.pessoa_repository, "atualizar", fake_atualizar_pessoa)
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "atualizar", fake_atualizar_barbeiro
    )

    payload = BarbeiroCompletoUpdate(
        nome="Pedro Atualizado",
        cpf="55566677788",
        email="novo@ex.com",
        data_nascimento=date(1988, 11, 3),
        especialidade="Barba",
        ativo=False,
    )

    result = barbeiro_service.atualizar_barbeiro_completo(conn, 1, payload)

    assert result == {"barbeiro": barbeiro, "pessoa": pessoa}
    assert pessoa_payload == {
        "nome": "Pedro Atualizado",
        "cpf": "55566677788",
        "email": "novo@ex.com",
        "data_nascimento": date(1988, 11, 3),
    }
    assert barbeiro_payload == {"especialidade": "Barba", "ativo": False}
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_barbeiro_completo_falha_ao_atualizar_barbeiro_reverte_pessoa(monkeypatch):
    conn = FakeConn()
    barbeiro_atual = _barbeiro_row(pessoa_id=10)
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: barbeiro_atual,
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "atualizar",
        lambda _c, _id, _data: _pessoa_row(pessoa_id=10),
    )

    def fake_atualizar_barbeiro(_c, _id, _data):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "atualizar", fake_atualizar_barbeiro
    )

    with pytest.raises(RuntimeError):
        barbeiro_service.atualizar_barbeiro_completo(conn, 1, _payload())

    assert conn.rolled_back is True
    assert conn.committed is False


def test_atualizar_barbeiro_completo_barbeiro_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: None,
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.atualizar_barbeiro_completo(conn, 404, _payload())

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_barbeiro_completo_pessoa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: _barbeiro_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: None,
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.atualizar_barbeiro_completo(conn, 1, _payload())

    assert exc.value.status_code == 404
    assert "Pessoa" in exc.value.detail
    assert conn.rolled_back is True


def test_atualizar_barbeiro_completo_cpf_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: _barbeiro_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_cpf",
        lambda _c, _v: _pessoa_row(pessoa_id=99),
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.atualizar_barbeiro_completo(
            conn,
            1,
            BarbeiroCompletoUpdate(cpf="99999999999"),
        )

    assert exc.value.status_code == 409
    assert "CPF" in exc.value.detail
    assert conn.rolled_back is True


def test_atualizar_barbeiro_completo_cpf_novo_disponivel_commita(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: _barbeiro_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "atualizar",
        lambda _c, _id, data: _pessoa_row(pessoa_id=10) | {"cpf": data["cpf"]},
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "atualizar",
        lambda _c, _id, _data: _barbeiro_row(pessoa_id=10),
    )

    result = barbeiro_service.atualizar_barbeiro_completo(
        conn,
        1,
        BarbeiroCompletoUpdate(cpf="99999999999"),
    )

    assert result["pessoa"]["cpf"] == "99999999999"
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_barbeiro_completo_email_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: _barbeiro_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_email",
        lambda _c, _v: _pessoa_row(pessoa_id=99),
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.atualizar_barbeiro_completo(
            conn,
            1,
            BarbeiroCompletoUpdate(email="duplicado@ex.com"),
        )

    assert exc.value.status_code == 409
    assert "Email" in exc.value.detail
    assert conn.rolled_back is True


def test_atualizar_barbeiro_completo_email_nulo_nao_verifica_duplicidade(monkeypatch):
    conn = FakeConn()
    chamou_email = False

    def fake_email(_c, _v):
        nonlocal chamou_email
        chamou_email = True
        return None

    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _id: _barbeiro_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "buscar_por_id",
        lambda _c, _id: _pessoa_row(pessoa_id=10),
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_email", fake_email
    )
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository,
        "atualizar",
        lambda _c, _id, data: _pessoa_row(pessoa_id=10) | {"email": data["email"]},
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository,
        "atualizar",
        lambda _c, _id, _data: _barbeiro_row(pessoa_id=10),
    )

    result = barbeiro_service.atualizar_barbeiro_completo(
        conn,
        1,
        BarbeiroCompletoUpdate(email=None),
    )

    assert result["pessoa"]["email"] is None
    assert chamou_email is False
    assert conn.committed is True
