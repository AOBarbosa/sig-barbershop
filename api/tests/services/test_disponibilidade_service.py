from datetime import time

import pytest
from fastapi import HTTPException

from app.schemas.disponibilidade_schema import (
    DiaSemana,
    DisponibilidadeCreate,
    DisponibilidadeUpdate,
)
from app.services import disponibilidade_service


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


def disp_row(disp_id=1, dia="SEGUNDA", hi=time(9, 0), hf=time(18, 0), barbeiro=1):
    return {
        "id_disponibilidade": disp_id,
        "BARBEIRO_PESSOA_id_pessoa": barbeiro,
        "dia_semana": dia,
        "hora_inicio": hi,
        "hora_fim": hf,
    }


def _payload(dia=DiaSemana.segunda, hi=time(9, 0), hf=time(18, 0)):
    return DisponibilidadeCreate(
        BARBEIRO_PESSOA_id_pessoa=1, dia_semana=dia, hora_inicio=hi, hora_fim=hf
    )


def test_buscar_disponibilidade_existente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: disp_row(),
    )

    assert disponibilidade_service.buscar_disponibilidade(conn, 1) == disp_row()


def test_buscar_disponibilidade_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: None,
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.buscar_disponibilidade(conn, 404)

    assert exc.value.status_code == 404


def test_listar_por_barbeiro_existente(monkeypatch):
    conn = FakeConn()
    rows = [disp_row()]
    monkeypatch.setattr(
        disponibilidade_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _i: {"id_barbeiro": 1},
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _i: rows,
    )

    assert disponibilidade_service.listar_por_barbeiro(conn, 1) == rows


def test_listar_por_barbeiro_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: None
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.listar_por_barbeiro(conn, 404)

    assert exc.value.status_code == 404


def test_criar_disponibilidade_controla_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _i: {"id_barbeiro": 1},
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _b: [],
    )
    created = disp_row()
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "criar",
        lambda _c, _d: created,
    )

    result = disponibilidade_service.criar_disponibilidade(conn, _payload())

    assert result == created
    assert conn.committed is True


def test_criar_disponibilidade_sem_barbeiro_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: None
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.criar_disponibilidade(conn, _payload())

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_criar_disponibilidade_dia_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.barbeiro_repository,
        "buscar_por_id",
        lambda _c, _i: {"id_barbeiro": 1},
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _b: [disp_row()],
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.criar_disponibilidade(conn, _payload())

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_atualizar_disponibilidade_existente(monkeypatch):
    conn = FakeConn()
    atual = disp_row()
    novo = disp_row() | {"hora_fim": time(19, 0)}

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
        conn, 1, DisponibilidadeUpdate(hora_fim=time(19, 0))
    )

    assert result == novo
    assert conn.committed is True


def test_atualizar_disponibilidade_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: None,
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.atualizar_disponibilidade(
            conn, 404, DisponibilidadeUpdate(hora_fim=time(19, 0))
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_disponibilidade_troca_dia_conflitante_retorna_409(monkeypatch):
    conn = FakeConn()
    atual = disp_row(disp_id=1, dia="SEGUNDA")
    outro = disp_row(disp_id=2, dia="TERCA")

    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: atual,
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "listar_por_barbeiro",
        lambda _c, _b: [outro],
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.atualizar_disponibilidade(
            conn, 1, DisponibilidadeUpdate(dia_semana=DiaSemana.terca)
        )

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_atualizar_disponibilidade_com_intervalo_invalido_retorna_422(monkeypatch):
    conn = FakeConn()
    atual = disp_row(hi=time(9, 0), hf=time(18, 0))

    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: atual,
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.atualizar_disponibilidade(
            conn, 1, DisponibilidadeUpdate(hora_fim=time(8, 0))
        )

    assert exc.value.status_code == 422
    assert conn.rolled_back is True


def test_deletar_disponibilidade_existente(monkeypatch):
    conn = FakeConn()
    called = []
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: disp_row(),
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "deletar",
        lambda _c, i: called.append(i),
    )

    disponibilidade_service.deletar_disponibilidade(conn, 1)

    assert called == [1]
    assert conn.committed is True


def test_deletar_disponibilidade_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: None,
    )

    with pytest.raises(HTTPException) as exc:
        disponibilidade_service.deletar_disponibilidade(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
