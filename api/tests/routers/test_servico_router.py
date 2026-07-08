import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import servico_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def servico_response(servico_id=1):
    return {
        "id_servico": servico_id,
        "nome": "Corte",
        "ativo": True,
        "preco": "40.00",
        "duracao_em_minutos": 45,
        "pontos_gerados": 4,
    }


def test_get_servicos_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    expected = [
        {
            "id_servico": 1,
            "nome": "Corte",
            "ativo": True,
            "preco": "40.00",
            "duracao_em_minutos": 45,
            "pontos_gerados": 4,
        }
    ]

    monkeypatch.setattr(servico_router.servico_service, "listar_servicos", lambda _conn: expected)

    response = client.get("/servicos")

    assert response.status_code == 200
    assert response.json() == expected
    clear_overrides()


def test_get_servico_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, servico_id):
        assert servico_id == 1
        return servico_response()

    monkeypatch.setattr(servico_router.servico_service, "buscar_servico", fake_buscar)

    response = client.get("/servicos/1")

    assert response.status_code == 200
    assert response.json()["id_servico"] == 1
    clear_overrides()


def test_get_servico_por_id_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, _servico_id):
        raise HTTPException(status_code=404, detail="Servico nao encontrado")

    monkeypatch.setattr(servico_router.servico_service, "buscar_servico", fake_buscar)

    response = client.get("/servicos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Servico nao encontrado"}
    clear_overrides()


def test_get_historico_servico_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    historico = [
        {
            "id_historico": 1,
            "SERVICO_id_servico": 1,
            "preco": "45.00",
            "duracao_em_minutos": 30,
            "pontos_gerados": 5,
            "data_inicio": "2026-07-02",
            "data_fim": None,
            "ativo": True,
        }
    ]

    def fake_listar_historico(_conn, servico_id):
        assert servico_id == 1
        return historico

    monkeypatch.setattr(
        servico_router.servico_service,
        "listar_historico_servico",
        fake_listar_historico,
    )

    response = client.get("/servicos/1/historico")

    assert response.status_code == 200
    assert response.json() == historico
    clear_overrides()


def test_get_historico_servico_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_listar_historico(_conn, _servico_id):
        raise HTTPException(status_code=404, detail="Servico nao encontrado")

    monkeypatch.setattr(
        servico_router.servico_service,
        "listar_historico_servico",
        fake_listar_historico,
    )

    response = client.get("/servicos/404/historico")

    assert response.status_code == 404
    assert response.json() == {"detail": "Servico nao encontrado"}
    clear_overrides()


def test_post_servicos_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    created = {
        "id_servico": 2,
        "nome": "Barba",
        "ativo": True,
        "preco": "35.00",
        "duracao_em_minutos": 30,
        "pontos_gerados": 3,
    }

    def fake_criar(_conn, payload):
        assert payload.nome == "Barba"
        return created

    monkeypatch.setattr(servico_router.servico_service, "criar_servico", fake_criar)

    response = client.post(
        "/servicos",
        json={
            "nome": "Barba",
            "ativo": True,
            "preco": 35,
            "duracao_em_minutos": 30,
            "pontos_gerados": 3,
        },
    )

    assert response.status_code == 201
    assert response.json()["id_servico"] == 2
    clear_overrides()


def test_post_servicos_rejeita_payload_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/servicos",
        json={
            "nome": "",
            "ativo": True,
        },
    )

    assert response.status_code == 422
    clear_overrides()


def test_put_servico_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, servico_id, payload):
        assert servico_id == 1
        assert payload.nome == "Corte premium"
        return servico_response() | {"nome": "Corte premium"}

    monkeypatch.setattr(servico_router.servico_service, "atualizar_servico", fake_atualizar)

    response = client.put(
        "/servicos/1",
        json={
            "nome": "Corte premium",
            "preco": 50,
            "duracao_em_minutos": 50,
            "pontos_gerados": 6,
        },
    )

    assert response.status_code == 200
    assert response.json()["nome"] == "Corte premium"
    clear_overrides()


def test_put_servico_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, _servico_id, _payload):
        raise HTTPException(status_code=404, detail="Servico nao encontrado")

    monkeypatch.setattr(servico_router.servico_service, "atualizar_servico", fake_atualizar)

    response = client.put("/servicos/404", json={"nome": "Corte premium"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Servico nao encontrado"}
    clear_overrides()


def test_put_servico_rejeita_payload_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.put("/servicos/1", json={"nome": ""})

    assert response.status_code == 422
    clear_overrides()


def test_delete_servico_sem_vinculo_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    deleted_ids = []

    monkeypatch.setattr(
        servico_router.servico_service,
        "deletar_servico",
        lambda _conn, servico_id: deleted_ids.append(servico_id),
    )

    response = client.delete("/servicos/1")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted_ids == [1]
    clear_overrides()


def test_delete_servico_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _servico_id):
        raise HTTPException(status_code=404, detail="Servico nao encontrado")

    monkeypatch.setattr(servico_router.servico_service, "deletar_servico", fake_deletar)

    response = client.delete("/servicos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Servico nao encontrado"}
    clear_overrides()


def test_delete_servico_repassa_conflito_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _servico_id):
        raise HTTPException(status_code=409, detail="Servico possui atendimentos vinculados")

    monkeypatch.setattr(servico_router.servico_service, "deletar_servico", fake_deletar)

    response = client.delete("/servicos/1")

    assert response.status_code == 409
    assert response.json() == {"detail": "Servico possui atendimentos vinculados"}
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(servico_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
