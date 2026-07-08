from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services import historico_pontos_service


class FakeConn:
    pass


def cliente_row(cliente_id=1):
    return {"id_cliente": cliente_id, "PESSOA_id_pessoa": 1}


def historico_row(historico_id=1):
    return {
        "id_historico": historico_id,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "pontos": 10,
        "tipo_movimentacao": "acumulo",
        "descricao": "Atendimento #1 CONCLUIDO",
        "data_movimentacao": datetime(2026, 7, 5, 9, 0),
    }


def fidelidade_row(pontos=10, servico_id=None, produto_id=None):
    return {
        "id_fidelidade": 1,
        "SERVICO_id_servico": servico_id,
        "PRODUTO_id_produto": produto_id,
        "pontos": pontos,
        "ativo": True,
    }


def test_buscar_saldo_pontos_cliente_existente_retorna_saldo(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(historico_pontos_service.cliente_repository, "buscar_por_id", lambda _c, _id: cliente_row())
    monkeypatch.setattr(historico_pontos_service.historico_pontos_repository, "calcular_saldo", lambda _c, _id: 25)

    result = historico_pontos_service.buscar_saldo_pontos(conn, 1)

    assert result == {"CLIENTE_PESSOA_id_pessoa": 1, "saldo": 25}


def test_buscar_saldo_pontos_cliente_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(historico_pontos_service.cliente_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        historico_pontos_service.buscar_saldo_pontos(conn, 404)

    assert exc.value.status_code == 404


def test_listar_historico_pontos_cliente_existente_retorna_extrato(monkeypatch):
    conn = FakeConn()
    rows = [historico_row()]
    monkeypatch.setattr(historico_pontos_service.cliente_repository, "buscar_por_id", lambda _c, _id: cliente_row())
    monkeypatch.setattr(historico_pontos_service.historico_pontos_repository, "listar_por_cliente", lambda _c, _id: rows)

    result = historico_pontos_service.listar_historico_pontos(conn, 1)

    assert result == rows


def test_listar_historico_pontos_cliente_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(historico_pontos_service.cliente_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        historico_pontos_service.listar_historico_pontos(conn, 404)

    assert exc.value.status_code == 404


def test_acumular_pontos_atendimento_soma_pontos_dos_servicos_com_regra(monkeypatch):
    conn = FakeConn()
    servicos = [
        {"id_atendimento_servico": 1, "ATENDIMENTO_id_atendimento": 1, "SERVICO_id_servico": 10, "preco_cobrado": 35},
        {"id_atendimento_servico": 2, "ATENDIMENTO_id_atendimento": 1, "SERVICO_id_servico": 20, "preco_cobrado": 50},
    ]
    monkeypatch.setattr(
        historico_pontos_service.atendimento_servico_repository,
        "listar_por_atendimento",
        lambda _c, _id: servicos,
    )

    def fake_buscar_por_servico(_conn, servico_id):
        return fidelidade_row(pontos=5, servico_id=servico_id) if servico_id == 10 else None

    monkeypatch.setattr(historico_pontos_service.fidelidade_repository, "buscar_por_servico", fake_buscar_por_servico)

    criados = []
    monkeypatch.setattr(
        historico_pontos_service.historico_pontos_repository,
        "criar",
        lambda _c, cliente_id, pontos, tipo, descricao: criados.append((cliente_id, pontos, tipo, descricao)),
    )

    result = historico_pontos_service.acumular_pontos_atendimento(conn, 1, 7)

    assert result == 5
    assert criados == [(7, 5, "acumulo", "Atendimento #1 CONCLUIDO")]


def test_acumular_pontos_atendimento_nao_grava_quando_nenhum_servico_tem_regra(monkeypatch):
    conn = FakeConn()
    servicos = [{"id_atendimento_servico": 1, "ATENDIMENTO_id_atendimento": 1, "SERVICO_id_servico": 10, "preco_cobrado": 35}]
    monkeypatch.setattr(
        historico_pontos_service.atendimento_servico_repository,
        "listar_por_atendimento",
        lambda _c, _id: servicos,
    )
    monkeypatch.setattr(historico_pontos_service.fidelidade_repository, "buscar_por_servico", lambda _c, _id: None)

    criados = []
    monkeypatch.setattr(
        historico_pontos_service.historico_pontos_repository,
        "criar",
        lambda _c, *args: criados.append(args),
    )

    result = historico_pontos_service.acumular_pontos_atendimento(conn, 1, 7)

    assert result == 0
    assert criados == []


def test_acumular_pontos_venda_soma_pontos_multiplicados_pela_quantidade(monkeypatch):
    conn = FakeConn()
    produtos = [
        {"id_venda_produto": 1, "VENDA_id_venda": 1, "PRODUTO_id_produto": 30, "quantidade": 3, "preco_unitario": 10},
        {"id_venda_produto": 2, "VENDA_id_venda": 1, "PRODUTO_id_produto": 40, "quantidade": 2, "preco_unitario": 5},
    ]
    monkeypatch.setattr(
        historico_pontos_service.venda_produto_repository,
        "listar_por_venda",
        lambda _c, _id: produtos,
    )

    def fake_buscar_por_produto(_conn, produto_id):
        return fidelidade_row(pontos=2, produto_id=produto_id) if produto_id == 30 else None

    monkeypatch.setattr(historico_pontos_service.fidelidade_repository, "buscar_por_produto", fake_buscar_por_produto)

    criados = []
    monkeypatch.setattr(
        historico_pontos_service.historico_pontos_repository,
        "criar",
        lambda _c, cliente_id, pontos, tipo, descricao: criados.append((cliente_id, pontos, tipo, descricao)),
    )

    result = historico_pontos_service.acumular_pontos_venda(conn, 1, 9)

    assert result == 6
    assert criados == [(9, 6, "acumulo", "Venda #1 PAGA")]


def test_acumular_pontos_venda_nao_grava_quando_nenhum_produto_tem_regra(monkeypatch):
    conn = FakeConn()
    produtos = [{"id_venda_produto": 1, "VENDA_id_venda": 1, "PRODUTO_id_produto": 30, "quantidade": 3, "preco_unitario": 10}]
    monkeypatch.setattr(
        historico_pontos_service.venda_produto_repository,
        "listar_por_venda",
        lambda _c, _id: produtos,
    )
    monkeypatch.setattr(historico_pontos_service.fidelidade_repository, "buscar_por_produto", lambda _c, _id: None)

    criados = []
    monkeypatch.setattr(
        historico_pontos_service.historico_pontos_repository,
        "criar",
        lambda _c, *args: criados.append(args),
    )

    result = historico_pontos_service.acumular_pontos_venda(conn, 1, 9)

    assert result == 0
    assert criados == []
