from decimal import Decimal

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import atendimento_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def vinculo_response():
    return {
        "id_atendimento_servico": 10,
        "ATENDIMENTO_id_atendimento": 1,
        "SERVICO_id_servico": 2,
        "preco_cobrado": Decimal("35.00"),
    }


def test_get_servicos_atendimento_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "listar_servicos_atendimento",
        lambda _conn, atendimento_id: [vinculo_response() | {"ATENDIMENTO_id_atendimento": atendimento_id}],
    )

    response = client.get("/atendimentos/1/servicos")

    assert response.status_code == 200
    assert response.json()[0]["ATENDIMENTO_id_atendimento"] == 1
    clear_overrides()


def test_get_servicos_atendimento_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_listar(_conn, _atendimento_id):
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

    monkeypatch.setattr(atendimento_router.atendimento_service, "listar_servicos_atendimento", fake_listar)

    response = client.get("/atendimentos/404/servicos")

    assert response.status_code == 404
    assert response.json() == {"detail": "Atendimento nao encontrado"}
    clear_overrides()


def test_post_servico_atendimento_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_adicionar(_conn, atendimento_id, payload):
        assert atendimento_id == 1
        assert payload.SERVICO_id_servico == 2
        return vinculo_response()

    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "adicionar_servico_atendimento",
        fake_adicionar,
    )

    response = client.post("/atendimentos/1/servicos", json={"SERVICO_id_servico": 2})

    assert response.status_code == 201
    assert response.json()["preco_cobrado"] == "35.00"
    clear_overrides()


def test_post_servico_atendimento_rejeita_payload_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post("/atendimentos/1/servicos", json={"SERVICO_id_servico": 0})

    assert response.status_code == 422
    clear_overrides()


def test_post_servico_atendimento_repassa_409_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_adicionar(_conn, _atendimento_id, _payload):
        raise HTTPException(status_code=409, detail="Servico ja vinculado ao atendimento")

    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "adicionar_servico_atendimento",
        fake_adicionar,
    )

    response = client.post("/atendimentos/1/servicos", json={"SERVICO_id_servico": 2})

    assert response.status_code == 409
    assert response.json() == {"detail": "Servico ja vinculado ao atendimento"}
    clear_overrides()


def test_delete_servico_atendimento_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    removed = []
    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "remover_servico_atendimento",
        lambda _conn, atendimento_id, servico_id: removed.append((atendimento_id, servico_id)),
    )

    response = client.delete("/atendimentos/1/servicos/2")

    assert response.status_code == 204
    assert response.content == b""
    assert removed == [(1, 2)]
    clear_overrides()


def test_delete_servico_atendimento_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_remover(_conn, _atendimento_id, _servico_id):
        raise HTTPException(status_code=404, detail="Servico nao vinculado ao atendimento")

    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "remover_servico_atendimento",
        fake_remover,
    )

    response = client.delete("/atendimentos/1/servicos/2")

    assert response.status_code == 404
    assert response.json() == {"detail": "Servico nao vinculado ao atendimento"}
    clear_overrides()
