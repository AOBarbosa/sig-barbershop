import inspect

from fastapi import HTTPException

from app.dependencies import get_current_user_opcional, get_db, require_funcionario
from app.main import app
from app.routers import produto_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def _usuario_admin():
    return {"id_pessoa": 1, "nome": "Admin", "email": "admin@ex.com", "role": "admin"}


def _usuario_funcionario():
    return {"id_pessoa": 99, "nome": "Func", "email": "f@ex.com", "role": "funcionario"}


def _override_admin_opcional():
    app.dependency_overrides.update(
        {get_db: override_db, get_current_user_opcional: _usuario_admin}
    )


def _override_funcionario():
    app.dependency_overrides.update(
        {get_db: override_db, require_funcionario: _usuario_funcionario}
    )


def produto_response(produto_id=1):
    return {
        "id_produto": produto_id,
        "nome": "Pomada modeladora",
        "categoria": "Finalizador",
        "ativo": True,
        "preco_venda": "45.00",
        "preco_custo": "25.00",
        "pontos_gerados": 5,
    }


def test_get_produtos_delega_para_service(client, monkeypatch):
    _override_admin_opcional()
    expected = [
        {
            "id_produto": 1,
            "nome": "Pomada modeladora",
            "categoria": "Finalizador",
            "ativo": True,
            "preco_venda": "45.00",
            "preco_custo": "25.00",
            "pontos_gerados": 5,
        }
    ]

    monkeypatch.setattr(produto_router.produto_service, "listar_produtos", lambda _conn: expected)

    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json() == expected
    clear_overrides()


def test_get_produto_por_id_delega_para_service(client, monkeypatch):
    _override_admin_opcional()

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


def test_get_historico_produto_delega_para_service(client, monkeypatch):
    _override_admin_opcional()
    expected = [
        {
            "id_historico": 1,
            "PRODUTO_id_produto": 1,
            "preco_venda": "45.00",
            "preco_custo": "25.00",
            "pontos_gerados": 5,
            "data_inicio": "2026-07-02",
            "data_fim": None,
            "ativo": True,
        }
    ]

    def fake_listar_historico(_conn, produto_id):
        assert produto_id == 1
        return expected

    monkeypatch.setattr(
        produto_router.produto_service, "listar_historico_produto", fake_listar_historico
    )

    response = client.get("/produtos/1/historico")

    assert response.status_code == 200
    assert response.json() == expected
    clear_overrides()


def test_get_historico_produto_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_listar_historico(_conn, _produto_id):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(
        produto_router.produto_service, "listar_historico_produto", fake_listar_historico
    )

    response = client.get("/produtos/404/historico")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_post_produtos_valida_payload_e_retorna_201(client, monkeypatch):
    _override_funcionario()
    created = {
        "id_produto": 2,
        "nome": "Shampoo",
        "categoria": "Higiene",
        "ativo": True,
        "preco_venda": "35.00",
        "preco_custo": "20.00",
        "pontos_gerados": 3,
    }

    def fake_criar(_conn, payload):
        assert payload.nome == "Shampoo"
        assert payload.categoria == "Higiene"
        return created

    monkeypatch.setattr(produto_router.produto_service, "criar_produto", fake_criar)

    response = client.post(
        "/produtos",
        json={
            "nome": "Shampoo",
            "categoria": "Higiene",
            "ativo": True,
            "preco_venda": 35,
            "preco_custo": 20,
            "pontos_gerados": 3,
        },
    )

    assert response.status_code == 201
    assert response.json()["id_produto"] == 2
    clear_overrides()


def test_post_produtos_rejeita_payload_invalido(client):
    _override_funcionario()

    response = client.post(
        "/produtos",
        json={
            "nome": "",
            "ativo": True,
        },
    )

    assert response.status_code == 422
    clear_overrides()


def test_put_produto_delega_para_service(client, monkeypatch):
    _override_funcionario()

    def fake_atualizar(_conn, produto_id, payload):
        assert produto_id == 1
        assert payload.nome == "Pomada premium"
        return produto_response() | {"nome": "Pomada premium"}

    monkeypatch.setattr(produto_router.produto_service, "atualizar_produto", fake_atualizar)

    response = client.put(
        "/produtos/1",
        json={
            "nome": "Pomada premium",
            "categoria": "Finalizador",
            "preco_venda": 55,
            "preco_custo": 30,
            "pontos_gerados": 7,
        },
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Pomada premium"
    clear_overrides()


def test_put_produto_repassa_404_do_service(client, monkeypatch):
    _override_funcionario()

    def fake_atualizar(_conn, _produto_id, _payload):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(produto_router.produto_service, "atualizar_produto", fake_atualizar)

    response = client.put("/produtos/404", json={"nome": "Pomada premium"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_put_produto_rejeita_payload_invalido(client):
    _override_funcionario()

    response = client.put("/produtos/1", json={"nome": ""})

    assert response.status_code == 422
    clear_overrides()


def test_delete_produto_sem_vinculo_retorna_204(client, monkeypatch):
    _override_funcionario()
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
    _override_funcionario()

    def fake_deletar(_conn, _produto_id):
        raise HTTPException(status_code=404, detail="Produto nao encontrado")

    monkeypatch.setattr(produto_router.produto_service, "deletar_produto", fake_deletar)

    response = client.delete("/produtos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto nao encontrado"}
    clear_overrides()


def test_delete_produto_repassa_conflito_do_service(client, monkeypatch):
    _override_funcionario()

    def fake_deletar(_conn, _produto_id):
        raise HTTPException(status_code=409, detail="Produto possui movimentacoes vinculadas")

    monkeypatch.setattr(produto_router.produto_service, "deletar_produto", fake_deletar)

    response = client.delete("/produtos/1")

    assert response.status_code == 409
    assert response.json() == {"detail": "Produto possui movimentacoes vinculadas"}
    clear_overrides()


def test_get_produtos_sem_login_oculta_preco_custo(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        produto_router.produto_service, "listar_produtos", lambda _c: [produto_response()]
    )

    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json()[0]["preco_custo"] is None
    clear_overrides()


def test_get_produtos_como_funcionario_tambem_oculta_preco_custo(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user_opcional] = _usuario_funcionario
    monkeypatch.setattr(
        produto_router.produto_service, "listar_produtos", lambda _c: [produto_response()]
    )

    response = client.get("/produtos")

    assert response.status_code == 200
    assert response.json()[0]["preco_custo"] is None
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(produto_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
