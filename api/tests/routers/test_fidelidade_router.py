import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import fidelidade_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def fidelidade_response(fidelidade_id=1):
    return {
        "id_fidelidade": fidelidade_id,
        "SERVICO_id_servico": 7,
        "PRODUTO_id_produto": None,
        "pontos_acumulados": 10,
        "pontos_uso": 0,
        "ativo": True,
    }


def test_get_fidelidades_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    expected = [fidelidade_response()]

    monkeypatch.setattr(
        fidelidade_router.fidelidade_service, "listar_fidelidades", lambda _conn: expected
    )

    response = client.get("/fidelidades")

    assert response.status_code == 200
    assert response.json() == expected
    clear_overrides()


def test_get_fidelidade_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, fidelidade_id):
        assert fidelidade_id == 1
        return fidelidade_response()

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "buscar_fidelidade", fake_buscar)

    response = client.get("/fidelidades/1")

    assert response.status_code == 200
    assert response.json()["id_fidelidade"] == 1
    clear_overrides()


def test_get_fidelidade_por_id_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, _fidelidade_id):
        raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "buscar_fidelidade", fake_buscar)

    response = client.get("/fidelidades/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Fidelidade nao encontrada"}
    clear_overrides()


def test_post_fidelidades_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    created = fidelidade_response(fidelidade_id=2)

    def fake_criar(_conn, payload):
        assert payload.SERVICO_id_servico == 7
        assert payload.pontos_acumulados == 10
        return created

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "criar_fidelidade", fake_criar)

    response = client.post(
        "/fidelidades",
        json={"SERVICO_id_servico": 7, "pontos_acumulados": 10},
    )

    assert response.status_code == 201
    assert response.json()["id_fidelidade"] == 2
    clear_overrides()


def test_post_fidelidades_rejeita_payload_com_pontos_invalidos(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/fidelidades",
        json={"SERVICO_id_servico": 7, "pontos_acumulados": -1},
    )

    assert response.status_code == 422
    clear_overrides()


def test_post_fidelidades_repassa_422_do_service_quando_viola_xor(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_criar(_conn, _payload):
        raise HTTPException(
            status_code=422,
            detail="Fidelidade deve referenciar exatamente um de SERVICO ou PRODUTO",
        )

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "criar_fidelidade", fake_criar)

    response = client.post(
        "/fidelidades",
        json={"SERVICO_id_servico": 7, "PRODUTO_id_produto": 5, "pontos_acumulados": 10},
    )

    assert response.status_code == 422
    clear_overrides()


def test_put_fidelidade_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, fidelidade_id, payload):
        assert fidelidade_id == 1
        assert payload.pontos_acumulados == 20
        return fidelidade_response() | {"pontos_acumulados": 20}

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "atualizar_fidelidade", fake_atualizar)

    response = client.put("/fidelidades/1", json={"pontos_acumulados": 20})

    assert response.status_code == 200
    assert response.json()["pontos_acumulados"] == 20
    clear_overrides()


def test_put_fidelidade_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, _fidelidade_id, _payload):
        raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "atualizar_fidelidade", fake_atualizar)

    response = client.put("/fidelidades/404", json={"pontos_acumulados": 20})

    assert response.status_code == 404
    assert response.json() == {"detail": "Fidelidade nao encontrada"}
    clear_overrides()


def test_put_fidelidade_repassa_422_do_service_quando_viola_xor(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, _fidelidade_id, _payload):
        raise HTTPException(
            status_code=422,
            detail="Fidelidade deve referenciar exatamente um de SERVICO ou PRODUTO",
        )

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "atualizar_fidelidade", fake_atualizar)

    response = client.put("/fidelidades/1", json={"PRODUTO_id_produto": 5})

    assert response.status_code == 422
    clear_overrides()


def test_put_fidelidade_rejeita_payload_com_pontos_invalidos(client):
    app.dependency_overrides[get_db] = override_db

    response = client.put("/fidelidades/1", json={"pontos_acumulados": -1})

    assert response.status_code == 422
    clear_overrides()


def test_delete_fidelidade_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    deleted_ids = []

    monkeypatch.setattr(
        fidelidade_router.fidelidade_service,
        "deletar_fidelidade",
        lambda _conn, fidelidade_id: deleted_ids.append(fidelidade_id),
    )

    response = client.delete("/fidelidades/1")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted_ids == [1]
    clear_overrides()


def test_delete_fidelidade_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _fidelidade_id):
        raise HTTPException(status_code=404, detail="Fidelidade nao encontrada")

    monkeypatch.setattr(fidelidade_router.fidelidade_service, "deletar_fidelidade", fake_deletar)

    response = client.delete("/fidelidades/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Fidelidade nao encontrada"}
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(fidelidade_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
