from datetime import date, datetime

import pytest
from fastapi import HTTPException

from app.schemas.pessoa_schema import PessoaCreate, PessoaUpdate
from app.services import pessoa_service


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


def pessoa_row(pessoa_id=1, cpf="12345678901", email="f@ex.com"):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": cpf,
        "email": email,
        "data_nascimento": date(1990, 1, 1),
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def _payload(cpf="12345678901", email="f@ex.com"):
    return PessoaCreate(
        nome="Fulano",
        cpf=cpf,
        email=email,
        data_nascimento=date(1990, 1, 1),
    )


def test_listar_pessoas_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [pessoa_row()]
    monkeypatch.setattr(pessoa_service.pessoa_repository, "listar", lambda _c: rows)

    result = pessoa_service.listar_pessoas(conn)

    assert result == rows
    assert conn.started is False


def test_buscar_pessoa_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    p = pessoa_row()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: p)

    assert pessoa_service.buscar_pessoa(conn, 1) == p
    assert conn.started is False


def test_buscar_pessoa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.buscar_pessoa(conn, 404)

    assert exc.value.status_code == 404


def test_criar_pessoa_controla_transacao_e_retorna_registro(monkeypatch):
    conn = FakeConn()
    created = pessoa_row(pessoa_id=1)

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "criar", lambda _c, _d: created)

    result = pessoa_service.criar_pessoa(conn, _payload())

    assert result == created
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_pessoa_com_cpf_duplicado_faz_rollback_e_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: pessoa_row()
    )

    with pytest.raises(HTTPException) as exc:
        pessoa_service.criar_pessoa(conn, _payload())

    assert exc.value.status_code == 409
    assert "CPF" in exc.value.detail
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_pessoa_com_email_duplicado_faz_rollback_e_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(
        pessoa_service.pessoa_repository, "buscar_por_email", lambda _c, _v: pessoa_row()
    )

    with pytest.raises(HTTPException) as exc:
        pessoa_service.criar_pessoa(conn, _payload())

    assert exc.value.status_code == 409
    assert "Email" in exc.value.detail
    assert conn.rolled_back is True


def test_criar_pessoa_sem_email_nao_verifica_email_duplicado(monkeypatch):
    conn = FakeConn()
    chamou_email = False

    def fake_email(_c, _v):
        nonlocal chamou_email
        chamou_email = True
        return None

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_email", fake_email)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "criar", lambda _c, _d: pessoa_row())

    pessoa_service.criar_pessoa(
        conn, PessoaCreate(nome="X", cpf="00000000000", email=None)
    )

    assert chamou_email is False


def test_criar_pessoa_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None)

    def fake_criar(_c, _d):
        raise RuntimeError("erro banco")

    monkeypatch.setattr(pessoa_service.pessoa_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        pessoa_service.criar_pessoa(conn, _payload())

    assert conn.rolled_back is True


def test_atualizar_pessoa_existente_controla_transacao(monkeypatch):
    conn = FakeConn()
    atual = pessoa_row()
    novo = pessoa_row() | {"nome": "Beltrano"}

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "atualizar", lambda _c, _i, _d: novo)

    result = pessoa_service.atualizar_pessoa(conn, 1, PessoaUpdate(nome="Beltrano"))

    assert result == novo
    assert conn.committed is True


def test_atualizar_pessoa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.atualizar_pessoa(conn, 999, PessoaUpdate(nome="X"))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_pessoa_com_novo_cpf_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    atual = pessoa_row(pessoa_id=1, cpf="11111111111")
    outra = pessoa_row(pessoa_id=2, cpf="22222222222")

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: outra)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.atualizar_pessoa(conn, 1, PessoaUpdate(cpf="22222222222"))

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_atualizar_pessoa_com_mesmo_cpf_nao_gera_conflito(monkeypatch):
    conn = FakeConn()
    atual = pessoa_row(pessoa_id=1, cpf="11111111111")
    novo = atual | {"nome": "Alterado"}

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "atualizar", lambda _c, _i, _d: novo)

    result = pessoa_service.atualizar_pessoa(
        conn, 1, PessoaUpdate(cpf="11111111111", nome="Alterado")
    )

    assert result == novo
    assert conn.committed is True


def test_deletar_pessoa_sem_vinculo_controla_transacao(monkeypatch):
    conn = FakeConn()
    deleted = []
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: pessoa_row())
    monkeypatch.setattr(pessoa_service.pessoa_repository, "existe_vinculo", lambda _c, _i: False)
    monkeypatch.setattr(
        pessoa_service.pessoa_repository, "deletar", lambda _c, i: deleted.append(i)
    )

    pessoa_service.deletar_pessoa(conn, 1)

    assert deleted == [1]
    assert conn.committed is True


def test_deletar_pessoa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.deletar_pessoa(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_pessoa_com_vinculo_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: pessoa_row())
    monkeypatch.setattr(pessoa_service.pessoa_repository, "existe_vinculo", lambda _c, _i: True)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.deletar_pessoa(conn, 1)

    assert exc.value.status_code == 409
    assert conn.rolled_back is True
