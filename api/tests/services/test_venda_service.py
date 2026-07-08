from datetime import datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.venda_schema import VendaCreate, VendaStatusUpdate
from app.services import venda_service


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


def venda_row(venda_id=1):
    return {
        "id_venda": venda_id,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "CAIXA_PESSOA_id_pessoa": 2,
        "data_hora": datetime(2026, 7, 5, 9, 0),
        "valor_total": Decimal("0.00"),
        "status": "ABERTA",
        "forma_pagamento": "PIX",
        "desconto": Decimal("0.00"),
    }


def venda_create(**overrides):
    data = {
        "CLIENTE_PESSOA_id_pessoa": 1,
        "CAIXA_PESSOA_id_pessoa": 2,
        "data_hora": datetime(2026, 7, 5, 9, 0),
        "forma_pagamento": "PIX",
    } | overrides
    return VendaCreate(**data)


def test_listar_vendas_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [venda_row()]
    monkeypatch.setattr(venda_service.venda_repository, "listar", lambda _conn: rows)

    result = venda_service.listar_vendas(conn)

    assert result == rows
    assert conn.started is False


def test_buscar_venda_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    venda = venda_row()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _conn, _id: venda)

    result = venda_service.buscar_venda(conn, 1)

    assert result == venda
    assert conn.started is False


def test_buscar_venda_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.buscar_venda(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_criar_venda_valida_refs_calcula_valor_total_e_commita(monkeypatch):
    conn = FakeConn()
    created = venda_row(venda_id=10)
    total_updates = []
    monkeypatch.setattr(venda_service.venda_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(venda_service.venda_repository, "caixa_existe", lambda _c, _id: True)
    monkeypatch.setattr(venda_service.venda_repository, "criar", lambda _c, data: created)
    monkeypatch.setattr(
        venda_service.venda_repository,
        "calcular_valor_total",
        lambda _c, venda_id: Decimal("0.00"),
    )

    def fake_atualizar_valor_total(_conn, venda_id, valor_total):
        total_updates.append((venda_id, valor_total))
        return created | {"valor_total": valor_total}

    monkeypatch.setattr(
        venda_service.venda_repository,
        "atualizar_valor_total",
        fake_atualizar_valor_total,
    )

    result = venda_service.criar_venda(
        conn,
        venda_create(),
    )

    assert result["valor_total"] == Decimal("0.00")
    assert total_updates == [(10, Decimal("0.00"))]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_venda_nao_aceita_cliente_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "cliente_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        venda_service.criar_venda(
            conn,
            venda_create(CLIENTE_PESSOA_id_pessoa=99),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_venda_nao_aceita_caixa_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(venda_service.venda_repository, "caixa_existe", lambda _c, _id: False)

    with pytest.raises(HTTPException) as exc:
        venda_service.criar_venda(
            conn,
            venda_create(CAIXA_PESSOA_id_pessoa=99),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True
    assert conn.committed is False


def test_criar_venda_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "cliente_existe", lambda _c, _id: True)
    monkeypatch.setattr(venda_service.venda_repository, "caixa_existe", lambda _c, _id: True)

    def fake_criar(_conn, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(venda_service.venda_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        venda_service.criar_venda(conn, venda_create())

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_status_venda_existente_commita(monkeypatch):
    conn = FakeConn()
    updated = venda_row() | {"status": "PAGA"}
    acumulos = []
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_repository, "atualizar_status", lambda _c, _id, status: updated)
    monkeypatch.setattr(
        venda_service.historico_pontos_service,
        "acumular_pontos_venda",
        lambda _c, venda_id, cliente_id: acumulos.append((venda_id, cliente_id)),
    )

    result = venda_service.atualizar_status_venda(conn, 1, VendaStatusUpdate(status="PAGA"))

    assert result["status"] == "PAGA"
    assert acumulos == [(1, venda_row()["CLIENTE_PESSOA_id_pessoa"])]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_status_venda_ja_PAGA_nao_acumula_pontos_novamente(monkeypatch):
    conn = FakeConn()
    atual = venda_row() | {"status": "PAGA"}
    acumulos = []
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: atual)
    monkeypatch.setattr(venda_service.venda_repository, "atualizar_status", lambda _c, _id, status: atual)
    monkeypatch.setattr(
        venda_service.historico_pontos_service,
        "acumular_pontos_venda",
        lambda _c, venda_id, cliente_id: acumulos.append((venda_id, cliente_id)),
    )

    venda_service.atualizar_status_venda(conn, 1, VendaStatusUpdate(status="PAGA"))

    assert acumulos == []
    assert conn.committed is True


def test_atualizar_status_venda_para_status_diferente_de_PAGA_nao_acumula_pontos(monkeypatch):
    conn = FakeConn()
    updated = venda_row() | {"status": "CANCELADA"}
    acumulos = []
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_repository, "atualizar_status", lambda _c, _id, status: updated)
    monkeypatch.setattr(
        venda_service.historico_pontos_service,
        "acumular_pontos_venda",
        lambda _c, venda_id, cliente_id: acumulos.append((venda_id, cliente_id)),
    )

    venda_service.atualizar_status_venda(conn, 1, VendaStatusUpdate(status="CANCELADA"))

    assert acumulos == []
    assert conn.committed is True


def test_atualizar_status_venda_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.atualizar_status_venda(conn, 404, VendaStatusUpdate(status="CANCELADA"))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_atualizar_status_venda_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())

    def fake_atualizar_status(_conn, _id, _status):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(venda_service.venda_repository, "atualizar_status", fake_atualizar_status)

    with pytest.raises(RuntimeError):
        venda_service.atualizar_status_venda(conn, 1, VendaStatusUpdate(status="CANCELADA"))

    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_venda_existente_commita(monkeypatch):
    conn = FakeConn()
    deleted_ids = []
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(
        venda_service.venda_repository,
        "deletar",
        lambda _c, venda_id: deleted_ids.append(venda_id),
    )

    result = venda_service.deletar_venda(conn, 1)

    assert result is None
    assert deleted_ids == [1]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_deletar_venda_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.deletar_venda(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_venda_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())

    def fake_deletar(_conn, _id):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(venda_service.venda_repository, "deletar", fake_deletar)

    with pytest.raises(RuntimeError):
        venda_service.deletar_venda(conn, 1)

    assert conn.committed is False
    assert conn.rolled_back is True
