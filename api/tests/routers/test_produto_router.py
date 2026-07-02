from decimal import Decimal
import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import produto_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def produto_response(produto_id=1):
    return {
        "id_produto": produto_id,
        "nome": "Pomada modeladora",
        "descricao": "Pomada efeito matte",
        "preco": Decimal("35.00"),
        "estoque": 20,
        "ativo": True,
    }


def test_get_produtos_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    expected = [
        {
            "id_produto": 1,
            "nome": "Pomada modeladora",
            "descricao": "Pomada efeito matte",
            "preco": "35.00",
            "estoque": 20,
            "ativo": True,
        }
    ]

    monkeypatch.setattr(produto_router.produto_service, "listar_produtos", lambda _conn: expected)

    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == expected
    clear_overrides()


def test_get_produto_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, produto_id):
        assert produto_id == 1
        return produto_response()

    monkeypatch.setattr(produto_router.produto_service, "buscar_produto", fake_buscar)

    response = client.get("/produtos/1")

    assert response.status_code == 200
    assert response.json()["id_produto"] == 1
    clear_overrides()


def test_get_produto_por_id_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, _produto_id):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(produto_router.produto_service, "buscar_produto", fake_buscar)

    response = client.get("/produtos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_post_produtos_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    created = {
        "id_produto": 2,
        "nome": "Shampoo",
        "descricao": "Shampoo anticaspa",
        "preco": Decimal("25.00"),
        "estoque": 15,
        "ativo": True,
    }

    def fake_criar(_conn, payload):
        assert payload.nome == "Shampoo"
        assert payload.preco == Decimal("25.00")
        return created

    monkeypatch.setattr(produto_router.produto_service, "criar_produto", fake_criar)

    response = client.post(
        "/produtos",
        json={
            "nome": "Shampoo",
            "descricao": "Shampoo anticaspa",
            "preco": "25.00",
            "estoque": 15,
            "ativo": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["id_produto"] == 2
    clear_overrides()


def test_post_produtos_rejeita_payload_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/produtos",
        json={
            "nome": "",
            "descricao": "Sem preco valido",
            "preco": "0.00",
            "estoque": -1,
            "ativo": True,
        },
    )

    assert response.status_code == 422
    clear_overrides()


def test_put_produto_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, produto_id, payload):
        assert produto_id == 1
        assert payload.nome == "Pomada premium"
        return produto_response() | {"nome": "Pomada premium"}

    monkeypatch.setattr(produto_router.produto_service, "atualizar_produto", fake_atualizar)

    response = client.put(
        "/produtos/1",
        json={"nome": "Pomada premium", "preco": "45.00"},
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Pomada premium"
    clear_overrides()


def test_put_produto_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, _produto_id, _payload):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(produto_router.produto_service, "atualizar_produto", fake_atualizar)

    response = client.put("/produtos/404", json={"nome": "Pomada premium"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_put_produto_rejeita_payload_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.put("/produtos/1", json={"preco": "-1.00"})

    assert response.status_code == 422
    clear_overrides()


def test_delete_produto_sem_vinculo_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    deleted_ids = []

    monkeypatch.setattr(
        produto_router.produto_service,
        "deletar_produto",
        lambda _conn, produto_id: deleted_ids.append(produto_id),
    )

    response = client.delete("/produtos/1")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted_ids == [1]
    clear_overrides()


def test_delete_produto_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _produto_id):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(produto_router.produto_service, "deletar_produto", fake_deletar)

    response = client.delete("/produtos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_delete_produto_repassa_conflito_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _produto_id):
        raise HTTPException(status_code=409, detail="Produto possui movimentacoes vinculadas")

    monkeypatch.setattr(produto_router.produto_service, "deletar_produto", fake_deletar)

    response = client.delete("/produtos/1")

    assert response.status_code == 409
    assert response.json() == {"detail": "Produto possui movimentacoes vinculadas"}
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(produto_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
