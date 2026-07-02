from datetime import datetime
from decimal import Decimal
import inspect

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


def atendimento_response(atendimento_id=1):
    return {
        "id_atendimento": atendimento_id,
        "CLIENTE_id_cliente": 1,
        "BARBEIRO_id_barbeiro": 2,
        "data_hora": datetime(2026, 7, 5, 9, 0),
        "status": "agendado",
        "valor_total": Decimal("0.00"),
        "observacao": "Primeiro atendimento",
    }


def test_get_atendimentos_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "listar_atendimentos",
        lambda _conn: [atendimento_response()],
    )

    response = client.get("/atendimentos")

    assert response.status_code == 200
    assert response.json()[0]["id_atendimento"] == 1
    clear_overrides()


def test_get_atendimento_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, atendimento_id):
        assert atendimento_id == 1
        return atendimento_response()

    monkeypatch.setattr(atendimento_router.atendimento_service, "buscar_atendimento", fake_buscar)

    response = client.get("/atendimentos/1")

    assert response.status_code == 200
    assert response.json()["id_atendimento"] == 1
    clear_overrides()


def test_get_atendimento_por_id_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, _atendimento_id):
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

    monkeypatch.setattr(atendimento_router.atendimento_service, "buscar_atendimento", fake_buscar)

    response = client.get("/atendimentos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Atendimento nao encontrado"}
    clear_overrides()


def test_post_atendimento_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_criar(_conn, payload):
        assert payload.CLIENTE_id_cliente == 1
        assert not hasattr(payload, "valor_total")
        return atendimento_response()

    monkeypatch.setattr(atendimento_router.atendimento_service, "criar_atendimento", fake_criar)

    response = client.post(
        "/atendimentos",
        json={
            "CLIENTE_id_cliente": 1,
            "BARBEIRO_id_barbeiro": 2,
            "data_hora": "2026-07-05T09:00:00",
            "observacao": "Primeiro atendimento",
        },
    )

    assert response.status_code == 201
    assert response.json()["valor_total"] == "0.00"
    clear_overrides()


def test_post_atendimento_rejeita_valor_total_do_cliente(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/atendimentos",
        json={
            "CLIENTE_id_cliente": 1,
            "BARBEIRO_id_barbeiro": 2,
            "data_hora": "2026-07-05T09:00:00",
            "valor_total": "999.00",
        },
    )

    assert response.status_code == 422
    clear_overrides()


def test_put_atendimento_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, atendimento_id, payload):
        assert atendimento_id == 1
        assert payload.observacao == "Remarcado"
        return atendimento_response() | {"observacao": "Remarcado"}

    monkeypatch.setattr(atendimento_router.atendimento_service, "atualizar_atendimento", fake_atualizar)

    response = client.put("/atendimentos/1", json={"observacao": "Remarcado"})

    assert response.status_code == 200
    assert response.json()["observacao"] == "Remarcado"
    clear_overrides()


def test_put_atendimento_rejeita_valor_total_do_cliente(client):
    app.dependency_overrides[get_db] = override_db

    response = client.put("/atendimentos/1", json={"valor_total": "100.00"})

    assert response.status_code == 422
    clear_overrides()


def test_put_atendimento_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_atualizar(_conn, _atendimento_id, _payload):
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

    monkeypatch.setattr(atendimento_router.atendimento_service, "atualizar_atendimento", fake_atualizar)

    response = client.put("/atendimentos/404", json={"observacao": "x"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Atendimento nao encontrado"}
    clear_overrides()


def test_patch_status_atendimento_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_status(_conn, atendimento_id, payload):
        assert atendimento_id == 1
        assert payload.status == "concluido"
        return atendimento_response() | {"status": "concluido"}

    monkeypatch.setattr(atendimento_router.atendimento_service, "atualizar_status_atendimento", fake_status)

    response = client.patch("/atendimentos/1/status", json={"status": "concluido"})

    assert response.status_code == 200
    assert response.json()["status"] == "concluido"
    clear_overrides()


def test_patch_status_atendimento_rejeita_status_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.patch("/atendimentos/1/status", json={"status": "finalizado"})

    assert response.status_code == 422
    clear_overrides()


def test_patch_status_atendimento_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_status(_conn, _atendimento_id, _payload):
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

    monkeypatch.setattr(atendimento_router.atendimento_service, "atualizar_status_atendimento", fake_status)

    response = client.patch("/atendimentos/404/status", json={"status": "cancelado"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Atendimento nao encontrado"}
    clear_overrides()


def test_delete_atendimento_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    deleted_ids = []
    monkeypatch.setattr(
        atendimento_router.atendimento_service,
        "deletar_atendimento",
        lambda _conn, atendimento_id: deleted_ids.append(atendimento_id),
    )

    response = client.delete("/atendimentos/1")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted_ids == [1]
    clear_overrides()


def test_delete_atendimento_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _atendimento_id):
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")

    monkeypatch.setattr(atendimento_router.atendimento_service, "deletar_atendimento", fake_deletar)

    response = client.delete("/atendimentos/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Atendimento nao encontrado"}
    clear_overrides()


def test_atendimento_router_nao_contem_sql():
    source = inspect.getsource(atendimento_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
