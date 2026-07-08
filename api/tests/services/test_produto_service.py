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
        "categoria": "Finalizador",
        "ativo": True,
        "preco_venda": 45.0,
        "preco_custo": 25.0,
        "pontos_gerados": 5,
    }
    historicos = []

    def fake_criar(received_conn, data):
        assert received_conn is conn
        assert data["nome"] == "Pomada modeladora"
        assert "preco_venda" not in data
        return {"id_produto": 1, "nome": "Pomada modeladora", "categoria": "Finalizador", "ativo": True}

    def fake_criar_historico(received_conn, **kwargs):
        assert received_conn is conn
        historicos.append(kwargs)

    def fake_buscar(received_conn, produto_id):
        assert received_conn is conn
        assert produto_id == 1
        return created

    monkeypatch.setattr(produto_service.produto_repository, "criar", fake_criar)
    monkeypatch.setattr(produto_service.historico_produto_repository, "criar", fake_criar_historico)
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", fake_buscar)

    result = produto_service.criar_produto(
        conn,
        ProdutoCreate(
            nome="Pomada modeladora",
            categoria="Finalizador",
            ativo=True,
            preco_venda=45,
            preco_custo=25,
            pontos_gerados=5,
        ),
    )

    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False
    assert historicos == [
        {
            "produto_id": 1,
            "preco_venda": 45,
            "preco_custo": 25,
            "pontos_gerados": 5,
            "ativo": True,
        }
    ]
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


def test_listar_historico_produto_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        produto_service.listar_historico_produto(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_listar_historico_produto_existente_delega_para_repository(monkeypatch):
    conn = FakeConn()
    rows = [{"id_historico": 1, "PRODUTO_id_produto": 1}]

    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1},
    )
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "listar_por_produto",
        lambda _conn, produto_id: rows,
    )

    result = produto_service.listar_historico_produto(conn, 1)

    assert result == rows
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
                categoria=None,
                ativo=True,
                preco_venda=45,
                preco_custo=25,
                pontos_gerados=5,
            ),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_produto_existente_controla_transacao_e_retorna_produto(monkeypatch):
    conn = FakeConn()
    updated = {
        "id_produto": 1,
        "nome": "Pomada premium",
        "categoria": "Finalizador",
        "ativo": True,
        "preco_venda": 55.0,
        "preco_custo": 30.0,
        "pontos_gerados": 7,
    }
    historicos_encerrados = []
    historicos_criados = []

    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {
            "id_produto": 1,
            "nome": "Pomada modeladora",
            "categoria": "Finalizador",
            "ativo": True,
        },
    )

    def fake_atualizar(received_conn, produto_id, data):
        assert received_conn is conn
        assert produto_id == 1
        assert data == {"nome": "Pomada premium"}
        return {"id_produto": 1, "nome": "Pomada premium", "categoria": "Finalizador", "ativo": True}

    def fake_buscar_vigente(received_conn, produto_id):
        assert received_conn is conn
        assert produto_id == 1
        return {
            "preco_venda": 45.0,
            "preco_custo": 25.0,
            "pontos_gerados": 5,
        }

    def fake_encerrar(received_conn, produto_id):
        historicos_encerrados.append((received_conn, produto_id))

    def fake_criar_historico(received_conn, **kwargs):
        historicos_criados.append(kwargs)

    monkeypatch.setattr(produto_service.produto_repository, "atualizar", fake_atualizar)
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "buscar_vigente",
        fake_buscar_vigente,
    )
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "encerrar_vigente",
        fake_encerrar,
    )
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "criar",
        fake_criar_historico,
    )
    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _conn, _id: updated)

    result = produto_service.atualizar_produto(
        conn,
        1,
        ProdutoUpdate(nome="Pomada premium", preco_venda=55, preco_custo=30, pontos_gerados=7),
    )

    assert result == updated
    assert historicos_encerrados == [(conn, 1)]
    assert historicos_criados == [
        {
            "produto_id": 1,
            "preco_venda": 55,
            "preco_custo": 30,
            "pontos_gerados": 7,
            "ativo": True,
        }
    ]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_produto_apenas_dados_principais_nao_cria_historico(monkeypatch):
    conn = FakeConn()
    historicos = []

    monkeypatch.setattr(
        produto_service.produto_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_produto": 1, "nome": "Pomada premium", "ativo": True},
    )
    monkeypatch.setattr(produto_service.produto_repository, "atualizar", lambda _c, _id, _d: None)
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "criar",
        lambda _conn, **kwargs: historicos.append(kwargs),
    )

    result = produto_service.atualizar_produto(conn, 1, ProdutoUpdate(nome="Pomada premium"))

    assert result["nome"] == "Pomada premium"
    assert historicos == []
    assert conn.committed is True


def test_atualizar_produto_apenas_historico_preserva_dados_vigentes(monkeypatch):
    conn = FakeConn()
    created = []
    updated = {"id_produto": 1, "preco_venda": 60, "preco_custo": 25, "pontos_gerados": 5}

    monkeypatch.setattr(produto_service.produto_repository, "buscar_por_id", lambda _c, _id: updated)
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "buscar_vigente",
        lambda _c, _id: {"preco_venda": 45, "preco_custo": 25, "pontos_gerados": 5},
    )
    monkeypatch.setattr(produto_service.historico_produto_repository, "encerrar_vigente", lambda *_: None)
    monkeypatch.setattr(
        produto_service.historico_produto_repository,
        "criar",
        lambda _conn, **kwargs: created.append(kwargs),
    )

    result = produto_service.atualizar_produto(conn, 1, ProdutoUpdate(preco_venda=60))

    assert result == updated
    assert created == [
        {
            "produto_id": 1,
            "preco_venda": 60,
            "preco_custo": 25,
            "pontos_gerados": 5,
            "ativo": True,
        }
    ]
    assert conn.committed is True


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
