from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.atendimento_schema import AtendimentoServicoCreate
from app.services import atendimento_service


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


def atendimento_row():
    return {"id_atendimento": 1, "valor_total": Decimal("0.00")}


def servico_row():
    return {"id_servico": 2, "preco": Decimal("35.00"), "ativo": True}


def vinculo_row():
    return {
        "id_atendimento_servico": 10,
        "ATENDIMENTO_id_atendimento": 1,
        "SERVICO_id_servico": 2,
        "preco_cobrado": Decimal("35.00"),
    }


def test_listar_servicos_atendimento_existente_retorna_vinculos(monkeypatch):
    conn = FakeConn()
    rows = [vinculo_row()]
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _conn, _id: atendimento_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "listar_por_atendimento",
        lambda _conn, _id: rows,
    )

    result = atendimento_service.listar_servicos_atendimento(conn, 1)

    assert result == rows
    assert conn.started is False


def test_listar_servicos_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.listar_servicos_atendimento(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_adicionar_servico_vincula_preco_atual_recalcula_total_e_commita(monkeypatch):
    conn = FakeConn()
    recalculos = []
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _conn, _id: atendimento_row(),
    )
    monkeypatch.setattr(
        atendimento_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: servico_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _conn, _atendimento_id, _servico_id: None,
    )

    def fake_criar(_conn, atendimento_id, servico_id, preco_cobrado):
        assert atendimento_id == 1
        assert servico_id == 2
        assert preco_cobrado == Decimal("35.00")
        return vinculo_row()

    def fake_recalcular(_conn, atendimento_id):
        recalculos.append(atendimento_id)
        return atendimento_row() | {"valor_total": Decimal("35.00")}

    monkeypatch.setattr(atendimento_service.atendimento_servico_repository, "criar", fake_criar)
    monkeypatch.setattr(atendimento_service, "_recalcular_valor_total", fake_recalcular)

    result = atendimento_service.adicionar_servico_atendimento(
        conn,
        1,
        AtendimentoServicoCreate(SERVICO_id_servico=2),
    )

    assert result == vinculo_row()
    assert recalculos == [1]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_adicionar_servico_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.adicionar_servico_atendimento(
            conn,
            404,
            AtendimentoServicoCreate(SERVICO_id_servico=2),
        )

    assert exc.value.status_code == 404
    assert conn.committed is False
    assert conn.rolled_back is True


def test_adicionar_servico_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _c, _id: atendimento_row(),
    )
    monkeypatch.setattr(atendimento_service.servico_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.adicionar_servico_atendimento(
            conn,
            1,
            AtendimentoServicoCreate(SERVICO_id_servico=404),
        )

    assert exc.value.status_code == 404
    assert conn.committed is False
    assert conn.rolled_back is True


def test_adicionar_servico_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _c, _id: atendimento_row(),
    )
    monkeypatch.setattr(atendimento_service.servico_repository, "buscar_por_id", lambda _c, _id: servico_row())
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _c, _atendimento_id, _servico_id: vinculo_row(),
    )

    with pytest.raises(HTTPException) as exc:
        atendimento_service.adicionar_servico_atendimento(
            conn,
            1,
            AtendimentoServicoCreate(SERVICO_id_servico=2),
        )

    assert exc.value.status_code == 409
    assert conn.committed is False
    assert conn.rolled_back is True


def test_adicionar_servico_faz_rollback_quando_recalculo_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _c, _id: atendimento_row(),
    )
    monkeypatch.setattr(atendimento_service.servico_repository, "buscar_por_id", lambda _c, _id: servico_row())
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _c, _atendimento_id, _servico_id: None,
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "criar",
        lambda _c, **_kwargs: vinculo_row(),
    )

    def fake_recalcular(_conn, _atendimento_id):
        raise RuntimeError("erro ao recalcular")

    monkeypatch.setattr(atendimento_service, "_recalcular_valor_total", fake_recalcular)

    with pytest.raises(RuntimeError):
        atendimento_service.adicionar_servico_atendimento(
            conn,
            1,
            AtendimentoServicoCreate(SERVICO_id_servico=2),
        )

    assert conn.committed is False
    assert conn.rolled_back is True


def test_remover_servico_remove_vinculo_recalcula_total_e_commita(monkeypatch):
    conn = FakeConn()
    recalculos = []
    removed = []
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _conn, _id: atendimento_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _conn, _atendimento_id, _servico_id: vinculo_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "deletar_por_ids",
        lambda _conn, atendimento_id, servico_id: removed.append((atendimento_id, servico_id)),
    )

    def fake_recalcular(_conn, atendimento_id):
        recalculos.append(atendimento_id)
        return atendimento_row()

    monkeypatch.setattr(atendimento_service, "_recalcular_valor_total", fake_recalcular)

    result = atendimento_service.remover_servico_atendimento(conn, 1, 2)

    assert result is None
    assert removed == [(1, 2)]
    assert recalculos == [1]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_remover_servico_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.remover_servico_atendimento(conn, 404, 2)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_remover_servico_sem_vinculo_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _c, _id: atendimento_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _c, _atendimento_id, _servico_id: None,
    )

    with pytest.raises(HTTPException) as exc:
        atendimento_service.remover_servico_atendimento(conn, 1, 2)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_remover_servico_faz_rollback_quando_recalculo_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _c, _id: atendimento_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "buscar_por_ids",
        lambda _c, _atendimento_id, _servico_id: vinculo_row(),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_servico_repository,
        "deletar_por_ids",
        lambda _c, _atendimento_id, _servico_id: None,
    )

    def fake_recalcular(_conn, _atendimento_id):
        raise RuntimeError("erro ao recalcular")

    monkeypatch.setattr(atendimento_service, "_recalcular_valor_total", fake_recalcular)

    with pytest.raises(RuntimeError):
        atendimento_service.remover_servico_atendimento(conn, 1, 2)

    assert conn.committed is False
    assert conn.rolled_back is True
