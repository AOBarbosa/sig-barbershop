from decimal import Decimal

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import venda_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def vinculo_response():
    return {
        "VENDA_id_venda": 1,
        "PRODUTO_id_produto": 2,
        "quantidade": 3,
        "preco_unitario": Decimal("10.00"),
    }


def test_get_produtos_venda_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        venda_router.venda_service,
        "listar_produtos_venda",
        lambda _conn, venda_id: [vinculo_response()],
    )

    response = client.get("/vendas/1/produtos")

    assert response.status_code == 200
    assert response.json()[0]["VENDA_id_venda"] == 1
    clear_overrides()


def test_get_produtos_venda_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_listar(_conn, _venda_id):
        raise HTTPException(status_code=404, detail="Venda nao encontrada")

    monkeypatch.setattr(venda_router.venda_service, "listar_produtos_venda", fake_listar)

    response = client.get("/vendas/404/produtos")

    assert response.status_code == 404
    clear_overrides()


def test_post_produto_venda_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_adicionar(_conn, venda_id, payload):
        assert venda_id == 1
        assert payload.PRODUTO_id_produto == 2
        assert payload.quantidade == 3
        assert not hasattr(payload, "preco_unitario")
        return vinculo_response()

    monkeypatch.setattr(venda_router.venda_service, "adicionar_produto_venda", fake_adicionar)

    response = client.post("/vendas/1/produtos", json={"PRODUTO_id_produto": 2, "quantidade": 3})

    assert response.status_code == 201
    assert response.json()["preco_unitario"] == "10.00"
    clear_overrides()


def test_post_produto_venda_rejeita_quantidade_invalida(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post("/vendas/1/produtos", json={"PRODUTO_id_produto": 2, "quantidade": 0})

    assert response.status_code == 422
    clear_overrides()


def test_post_produto_venda_repassa_422_estoque_insuficiente(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_adicionar(_conn, _venda_id, _payload):
        raise HTTPException(status_code=422, detail="Estoque insuficiente")

    monkeypatch.setattr(venda_router.venda_service, "adicionar_produto_venda", fake_adicionar)

    response = client.post("/vendas/1/produtos", json={"PRODUTO_id_produto": 2, "quantidade": 100})

    assert response.status_code == 422
    assert response.json() == {"detail": "Estoque insuficiente"}
    clear_overrides()


def test_post_produto_venda_repassa_409_produto_ja_vinculado(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_adicionar(_conn, _venda_id, _payload):
        raise HTTPException(status_code=409, detail="Produto ja vinculado a venda")

    monkeypatch.setattr(venda_router.venda_service, "adicionar_produto_venda", fake_adicionar)

    response = client.post("/vendas/1/produtos", json={"PRODUTO_id_produto": 2, "quantidade": 1})

    assert response.status_code == 409
    clear_overrides()


def test_delete_produto_venda_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    removidos = []
    monkeypatch.setattr(
        venda_router.venda_service,
        "remover_produto_venda",
        lambda _conn, venda_id, produto_id: removidos.append((venda_id, produto_id)),
    )

    response = client.delete("/vendas/1/produtos/2")

    assert response.status_code == 204
    assert response.content == b""
    assert removidos == [(1, 2)]
    clear_overrides()


def test_delete_produto_venda_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_remover(_conn, _venda_id, _produto_id):
        raise HTTPException(status_code=404, detail="Produto nao vinculado a venda")

    monkeypatch.setattr(venda_router.venda_service, "remover_produto_venda", fake_remover)

    response = client.delete("/vendas/1/produtos/99")

    assert response.status_code == 404
    clear_overrides()
