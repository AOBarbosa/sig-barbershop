from datetime import date, datetime, time

import pytest
from fastapi import HTTPException

from app.repositories import cliente_repository, pessoa_repository
from app.schemas.disponibilidade_schema import DiaSemana, DisponibilidadeUpdate
from app.schemas.pessoa_schema import PessoaUpdate
from app.services import disponibilidade_service, pessoa_service


class FakeCursor:
    def __init__(self, row=None):
        self.row = row
        self.closed = False

    def execute(self, _sql, _params=None):
        pass

    def fetchone(self):
        return self.row

    def close(self):
        self.closed = True


class FakeRepoConn:
    def __init__(self, cursor):
        self.fake_cursor = cursor

    def cursor(self, **_kwargs):
        return self.fake_cursor


class FakeServiceConn:
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    def start_transaction(self):
        pass

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


def disponibilidade_row(disp_id=1, dia="SEGUNDA"):
    return {
        "id_disponibilidade": disp_id,
        "BARBEIRO_PESSOA_id_pessoa": 1,
        "dia_semana": dia,
        "hora_inicio": time(9, 0),
        "hora_fim": time(18, 0),
    }


def test_cliente_vinculo_retorna_false_quando_select_nao_retorna_linha():
    cursor = FakeCursor(row=None)
    conn = FakeRepoConn(cursor)

    assert cliente_repository.existe_vinculo(conn, 3) is False
    assert cursor.closed is True


def test_pessoa_vinculo_retorna_false_quando_select_nao_retorna_linha():
    cursor = FakeCursor(row=None)
    conn = FakeRepoConn(cursor)

    assert pessoa_repository.existe_vinculo(conn, 7) is False
    assert cursor.closed is True


def test_atualizar_disponibilidade_troca_dia_sem_conflito(monkeypatch):
    conn = FakeServiceConn()
    atual = disponibilidade_row(disp_id=1, dia="SEGUNDA")
    novo = atual | {"dia_semana": "TERCA"}

    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: atual,
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _b: [atual],
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "atualizar",
        lambda _c, _i, _d: novo,
    )

    result = disponibilidade_service.atualizar_disponibilidade(
        conn, 1, DisponibilidadeUpdate(dia_semana=DiaSemana.terca)
    )

    assert result == novo
    assert conn.committed is True


def test_atualizar_disponibilidade_troca_dia_com_mesmo_registro(monkeypatch):
    conn = FakeServiceConn()
    atual = disponibilidade_row(disp_id=1, dia="SEGUNDA")
    novo = atual | {"dia_semana": "TERCA"}

    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: atual,
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _b: [disponibilidade_row(disp_id=1, dia="TERCA")],
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "atualizar",
        lambda _c, _i, _d: novo,
    )

    result = disponibilidade_service.atualizar_disponibilidade(
        conn, 1, DisponibilidadeUpdate(dia_semana=DiaSemana.terca)
    )

    assert result == novo
    assert conn.committed is True


def test_atualizar_pessoa_com_novo_cpf_disponivel(monkeypatch):
    conn = FakeServiceConn()
    atual = pessoa_row(pessoa_id=1, cpf="11111111111")
    novo = atual | {"cpf": "22222222222"}

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "atualizar", lambda _c, _i, _d: novo)

    result = pessoa_service.atualizar_pessoa(conn, 1, PessoaUpdate(cpf="22222222222"))

    assert result == novo
    assert conn.committed is True


def test_atualizar_pessoa_com_novo_email_duplicado_retorna_409(monkeypatch):
    conn = FakeServiceConn()
    atual = pessoa_row(pessoa_id=1, email="atual@ex.com")
    outra = pessoa_row(pessoa_id=2, email="novo@ex.com")

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_email", lambda _c, _v: outra)

    with pytest.raises(HTTPException) as exc:
        pessoa_service.atualizar_pessoa(conn, 1, PessoaUpdate(email="novo@ex.com"))

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_atualizar_pessoa_com_novo_email_disponivel(monkeypatch):
    conn = FakeServiceConn()
    atual = pessoa_row(pessoa_id=1, email="atual@ex.com")
    novo = atual | {"email": "novo@ex.com"}

    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: atual)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None)
    monkeypatch.setattr(pessoa_service.pessoa_repository, "atualizar", lambda _c, _i, _d: novo)

    result = pessoa_service.atualizar_pessoa(conn, 1, PessoaUpdate(email="novo@ex.com"))

    assert result == novo
    assert conn.committed is True
