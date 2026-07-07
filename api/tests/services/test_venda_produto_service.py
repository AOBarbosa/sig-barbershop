from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.venda_schema import VendaProdutoCreate
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


def venda_row():
    return {"id_venda": 1, "valor_total": Decimal("0.00")}


def produto_row(estoque=10, preco=Decimal("10.00")):
    return {"id_produto": 2, "preco": preco, "estoque": estoque, "ativo": True}


def vinculo_row():
    return {
        "id_venda_produto": 20,
        "VENDA_id_venda": 1,
        "PRODUTO_id_produto": 2,
        "quantidade": 3,
        "preco_unitario": Decimal("10.00"),
    }


def test_listar_produtos_venda_existente_retorna_vinculos(monkeypatch):
    conn = FakeConn()
    vinculos = [vinculo_row()]
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "listar_por_venda", lambda _c, _id: vinculos)

    result = venda_service.listar_produtos_venda(conn, 1)

    assert result == vinculos
    assert conn.started is False


def test_listar_produtos_venda_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.listar_produtos_venda(conn, 404)

    assert exc.value.status_code == 404


def test_adicionar_produto_venda_deduz_estoque_grava_preco_vigente_e_recalcula(monkeypatch):
    conn = FakeConn()
    produto = produto_row(estoque=10, preco=Decimal("10.00"))
    criado = vinculo_row()
    estoque_atualizado = []
    total_recalculado = []

    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto)
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: None)

    def fake_atualizar_produto(_conn, produto_id, data):
        estoque_atualizado.append((produto_id, data))

    monkeypatch.setattr(venda_service.produto_repository, "atualizar", fake_atualizar_produto)
    monkeypatch.setattr(venda_service.venda_produto_repository, "criar", lambda _c, **kwargs: criado)

    def fake_recalcular(_conn, venda_id):
        total_recalculado.append(venda_id)
        return venda_row()

    monkeypatch.setattr(venda_service, "_recalcular_valor_total", fake_recalcular)

    result = venda_service.adicionar_produto_venda(
        conn,
        1,
        VendaProdutoCreate(PRODUTO_id_produto=2, quantidade=3),
    )

    assert result == criado
    assert estoque_atualizado == [(2, {"estoque": 7})]
    assert total_recalculado == [1]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_adicionar_produto_venda_rejeita_estoque_insuficiente(monkeypatch):
    conn = FakeConn()
    produto = produto_row(estoque=2)
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto)
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.adicionar_produto_venda(
            conn,
            1,
            VendaProdutoCreate(PRODUTO_id_produto=2, quantidade=3),
        )

    assert exc.value.status_code == 422
    assert conn.rolled_back is True
    assert conn.committed is False


def test_adicionar_produto_venda_rejeita_venda_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.adicionar_produto_venda(
            conn,
            404,
            VendaProdutoCreate(PRODUTO_id_produto=2, quantidade=1),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_adicionar_produto_venda_rejeita_produto_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.adicionar_produto_venda(
            conn,
            1,
            VendaProdutoCreate(PRODUTO_id_produto=99, quantidade=1),
        )

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_adicionar_produto_venda_rejeita_produto_ja_vinculado(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: vinculo_row())

    with pytest.raises(HTTPException) as exc:
        venda_service.adicionar_produto_venda(
            conn,
            1,
            VendaProdutoCreate(PRODUTO_id_produto=2, quantidade=1),
        )

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_adicionar_produto_venda_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: None)
    monkeypatch.setattr(venda_service.produto_repository, "atualizar", lambda _c, _id, _data: None)

    def fake_criar(_conn, **_kwargs):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(venda_service.venda_produto_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        venda_service.adicionar_produto_venda(
            conn,
            1,
            VendaProdutoCreate(PRODUTO_id_produto=2, quantidade=1),
        )

    assert conn.committed is False
    assert conn.rolled_back is True


def test_remover_produto_venda_estorna_estoque_e_recalcula(monkeypatch):
    conn = FakeConn()
    produto = produto_row(estoque=7)
    deletados = []
    total_recalculado = []

    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: vinculo_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto)

    estoque_atualizado = []
    monkeypatch.setattr(
        venda_service.produto_repository,
        "atualizar",
        lambda _c, produto_id, data: estoque_atualizado.append((produto_id, data)),
    )
    monkeypatch.setattr(
        venda_service.venda_produto_repository,
        "deletar_por_ids",
        lambda _c, venda_id, produto_id: deletados.append((venda_id, produto_id)),
    )

    def fake_recalcular(_conn, venda_id):
        total_recalculado.append(venda_id)
        return venda_row()

    monkeypatch.setattr(venda_service, "_recalcular_valor_total", fake_recalcular)

    result = venda_service.remover_produto_venda(conn, 1, 2)

    assert result is None
    assert estoque_atualizado == [(2, {"estoque": 10})]
    assert deletados == [(1, 2)]
    assert total_recalculado == [1]
    assert conn.committed is True
    assert conn.rolled_back is False


def test_remover_produto_venda_rejeita_venda_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.remover_produto_venda(conn, 404, 2)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_remover_produto_venda_rejeita_vinculo_inexistente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: None)

    with pytest.raises(HTTPException) as exc:
        venda_service.remover_produto_venda(conn, 1, 99)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_remover_produto_venda_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(venda_service.venda_repository, "buscar_por_id", lambda _c, _id: venda_row())
    monkeypatch.setattr(venda_service.venda_produto_repository, "buscar_por_ids", lambda _c, _v, _p: vinculo_row())
    monkeypatch.setattr(venda_service.produto_repository, "buscar_por_id", lambda _c, _id: produto_row())

    def fake_atualizar(_conn, _id, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(venda_service.produto_repository, "atualizar", fake_atualizar)

    with pytest.raises(RuntimeError):
        venda_service.remover_produto_venda(conn, 1, 2)

    assert conn.committed is False
    assert conn.rolled_back is True
