from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.atendimento_schema import AtendimentoCreate, AtendimentoStatusUpdate, AtendimentoUpdate
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


def atendimento_row(atendimento_id=1):
    return {
        "id_atendimento": atendimento_id,
        "CLIENTE_id_cliente": 1,
        "BARBEIRO_id_barbeiro": 2,
        "data_hora": datetime(2026, 7, 5, 9, 0),
        "status": "agendado",
        "valor_total": Decimal("0.00"),
        "observacao": "Primeiro atendimento",
    }


def test_listar_atendimentos_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [atendimento_row()]
    monkeypatch.setattr(atendimento_service.atendimento_repository, "listar", lambda _conn: rows)

    result = atendimento_service.listar_atendimentos(conn)

    assert result == rows
    assert conn.started is False


def test_buscar_atendimento_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    atendimento = atendimento_row()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _conn, _id: atendimento,
    )

    result = atendimento_service.buscar_atendimento(conn, 1)

    assert result == atendimento
    assert conn.started is False


def test_buscar_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "buscar_por_id",
        lambda _conn, _id: None,
    )

    with pytest.raises(HTTPException) as exc:
        atendimento_service.buscar_atendimento(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_criar_atendimento_valida_refs_calcula_valor_total_e_commita(monkeypatch):
    conn = FakeConn()
    created = atendimento_row(atendimento_id=10)
    total_updates = []
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "barbeiro_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "criar", lambda _c, data: created)
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "calcular_valor_total",
        lambda _c, atendimento_id: Decimal("0.00"),
    )

    def fake_atualizar_valor_total(_conn, atendimento_id, valor_total):
        total_updates.append((atendimento_id, valor_total))
        return created | {"valor_total": valor_total}

    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "atualizar_valor_total",
        fake_atualizar_valor_total,
    )

    result = atendimento_service.criar_atendimento(
        conn,
        AtendimentoCreate(
            CLIENTE_id_cliente=1,
            BARBEIRO_id_barbeiro=2,
            data_hora=datetime(2026, 7, 5, 9, 0),
            observacao="Primeiro atendimento",
        ),
    )

    assert result["valor_total"] == Decimal("0.00")
    assert total_updates == [(10, Decimal("0.00"))]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_atendimento_nao_aceita_cliente_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.criar_atendimento(
            conn,
            AtendimentoCreate(CLIENTE_id_cliente=99, BARBEIRO_id_barbeiro=2, data_hora=datetime(2026, 7, 5, 9, 0)),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_atendimento_nao_aceita_barbeiro_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "barbeiro_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.criar_atendimento(
            conn,
            AtendimentoCreate(CLIENTE_id_cliente=1, BARBEIRO_id_barbeiro=99, data_hora=datetime(2026, 7, 5, 9, 0)),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_atendimento_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "barbeiro_existe", lambda _c, _id: True)

    def fake_criar(_conn, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(atendimento_service.atendimento_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        atendimento_service.criar_atendimento(
            conn,
            AtendimentoCreate(CLIENTE_id_cliente=1, BARBEIRO_id_barbeiro=2, data_hora=datetime(2026, 7, 5, 9, 0)),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_atendimento_existente_valida_refs_recalcula_total_e_commita(monkeypatch):
    conn = FakeConn()
    current = atendimento_row()
    updated = current | {"observacao": "Remarcado"}
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: current)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "barbeiro_existe", lambda _c, _id: True)
    monkeypatch.setattr(atendimento_service.atendimento_repository, "atualizar", lambda _c, _id, _data: updated)
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "calcular_valor_total",
        lambda _c, _id: Decimal("75.00"),
    )
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "atualizar_valor_total",
        lambda _c, _id, total: updated | {"valor_total": total},
    )

    result = atendimento_service.atualizar_atendimento(
        conn,
        1,
        AtendimentoUpdate(CLIENTE_id_cliente=1, BARBEIRO_id_barbeiro=2, observacao="Remarcado"),
    )

    assert result["valor_total"] == Decimal("75.00")
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.atualizar_atendimento(conn, 404, AtendimentoUpdate(observacao="x"))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
    assert conn.committed is False


def test_atualizar_atendimento_nao_aceita_cliente_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())
    monkeypatch.setattr(atendimento_service.atendimento_repository, "cliente_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.atualizar_atendimento(conn, 1, AtendimentoUpdate(CLIENTE_id_cliente=99))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_atendimento_nao_aceita_barbeiro_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())
    monkeypatch.setattr(atendimento_service.atendimento_repository, "barbeiro_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.atualizar_atendimento(conn, 1, AtendimentoUpdate(BARBEIRO_id_barbeiro=99))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_atendimento_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())

    def fake_atualizar(_conn, _id, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(atendimento_service.atendimento_repository, "atualizar", fake_atualizar)

    with pytest.raises(RuntimeError):
        atendimento_service.atualizar_atendimento(conn, 1, AtendimentoUpdate(observacao="x"))

    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_status_atendimento_existente_commita(monkeypatch):
    conn = FakeConn()
    updated = atendimento_row() | {"status": "concluido"}
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())
    monkeypatch.setattr(atendimento_service.atendimento_repository, "atualizar_status", lambda _c, _id, status: updated)

    result = atendimento_service.atualizar_status_atendimento(
        conn,
        1,
        AtendimentoStatusUpdate(status="concluido"),
    )

    assert result["status"] == "concluido"
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_status_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.atualizar_status_atendimento(
            conn,
            404,
            AtendimentoStatusUpdate(status="cancelado"),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_status_atendimento_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())

    def fake_atualizar_status(_conn, _id, _status):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(atendimento_service.atendimento_repository, "atualizar_status", fake_atualizar_status)

    with pytest.raises(RuntimeError):
        atendimento_service.atualizar_status_atendimento(
            conn,
            1,
            AtendimentoStatusUpdate(status="cancelado"),
        )

    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_atendimento_existente_commita(monkeypatch):
    conn = FakeConn()
    deleted_ids = []
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())
    monkeypatch.setattr(
        atendimento_service.atendimento_repository,
        "deletar",
        lambda _c, atendimento_id: deleted_ids.append(atendimento_id),
    )

    result = atendimento_service.deletar_atendimento(conn, 1)

    assert result is None
    assert deleted_ids == [1]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_deletar_atendimento_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        atendimento_service.deletar_atendimento(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_atendimento_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(atendimento_service.atendimento_repository, "buscar_por_id", lambda _c, _id: atendimento_row())

    def fake_deletar(_conn, _id):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(atendimento_service.atendimento_repository, "deletar", fake_deletar)

    with pytest.raises(RuntimeError):
        atendimento_service.deletar_atendimento(conn, 1)

    assert conn.committed is False
    assert conn.rolled_back is True
