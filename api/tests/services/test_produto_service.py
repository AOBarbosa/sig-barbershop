from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.produto_schema import ProdutoCreate, ProdutoUpdate
from app.services import produto_service


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


def test_criar_produto_controla_transacao_e_retorna_produto(monkeypatch):
    conn = FakeConn()
    created = {
        "id_produto": 1,
        "nome": "Pomada modeladora",
        "descricao": "Pomada efeito matte",
        "preco": Decimal("35.00"),
        "estoque": 20,
        "ativo": True,
    }

    def fake_criar(received_conn, data):
        assert received_conn is conn
        assert data["nome"] == "Pomada modeladora"
        return created

    monkeypatch.setattr(produto_service.produto_repository, "criar", fake_criar)

    result = produto_service.criar_produto(
        conn,
        ProdutoCreate(
            nome="Pomada modeladora",
            descricao="Pomada efeito matte",
            preco=Decimal("35.00"),
            estoque=20,
            ativo=True,
        ),
    )

    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False
    assert result == created


def test_listar_produtos_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [{"id_produto": 1}]
    monkeypatch.setattr(produto_service.produto_repository, "listar", lambda received_conn: rows)

    result = produto_service.listar_produtos(conn)

    assert result == rows
    assert conn.started is False
    assert conn.committed is False
    assert conn.rolled_back is False


def test_buscar_produto_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    produto = {"id_produto": 1, "nome": "Pomada modeladora"}
    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda received_conn, produto_id: produto,
    )

    result = produto_service.buscar_produto(conn, 1)

    assert result == produto
    assert conn.started is False


def test_buscar_produto_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        produto_service.buscar_produto(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_criar_produto_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()

    def fake_criar(_conn, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(produto_service.produto_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        produto_service.criar_produto(
            conn,
            ProdutoCreate(
                nome="Pomada modeladora",
                descricao=None,
                preco=Decimal("35.00"),
                estoque=20,
                ativo=True,
            ),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_produto_existente_controla_transacao_e_retorna_produto(monkeypatch):
    conn = FakeConn()
    updated = {"id_produto": 1, "nome": "Pomada premium"}

    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1, "nome": "Pomada modeladora"},
    )

    def fake_atualizar(received_conn, produto_id, data):
        assert received_conn is conn
        assert produto_id == 1
        assert data == {"nome": "Pomada premium"}
        return updated

    monkeypatch.setattr(produto_service.produto_repository, "atualizar", fake_atualizar)

    result = produto_service.atualizar_produto(
        conn,
        1,
        ProdutoUpdate(nome="Pomada premium"),
    )

    assert result == updated
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_produto_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        produto_service.atualizar_produto(
            conn,
            999,
            ProdutoUpdate(nome="Pomada premium"),
        )

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_produto_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1},
    )

    def fake_atualizar(_conn, _produto_id, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(produto_service.produto_repository, "atualizar", fake_atualizar)

    with pytest.raises(RuntimeError):
        produto_service.atualizar_produto(
            conn,
            1,
            ProdutoUpdate(nome="Pomada premium"),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_produto_existente_sem_vinculo_controla_transacao(monkeypatch):
    conn = FakeConn()
    deleted_ids = []
    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1},
    )
    monkeypatch.setattr(
        produto_service.produto_repository,
        "existe_venda_vinculada",
        lambda _conn, _id: False,
    )
    monkeypatch.setattr(
        produto_service.produto_repository,
        "deletar",
        lambda _conn, produto_id: deleted_ids.append(produto_id),
    )

    result = produto_service.deletar_produto(conn, 1)

    assert result is None
    assert deleted_ids == [1]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_deletar_produto_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        produto_service.deletar_produto(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_produto_com_venda_vinculada_faz_rollback_e_retorna_409(monkeypatch):
    conn = FakeConn()
    deleted = False

    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1},
    )
    monkeypatch.setattr(
        produto_service.produto_repository,
        "existe_venda_vinculada",
        lambda _conn, _id: True,
    )

    def fake_deletar(_conn, _id):
        nonlocal deleted
        deleted = True

    monkeypatch.setattr(produto_service.produto_repository, "deletar", fake_deletar)

    with pytest.raises(HTTPException) as exc:
        produto_service.deletar_produto(conn, 1)

    assert exc.value.status_code == 409
    assert deleted is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_produto_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1},
    )
    monkeypatch.setattr(
        produto_service.produto_repository,
        "existe_venda_vinculada",
        lambda _conn, _id: False,
    )

    def fake_deletar(_conn, _produto_id):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(produto_service.produto_repository, "deletar", fake_deletar)

    with pytest.raises(RuntimeError):
        produto_service.deletar_produto(conn, 1)

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True
