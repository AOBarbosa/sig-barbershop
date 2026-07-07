from datetime import datetime
from decimal import Decimal
import inspect

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


def venda_response(venda_id=1):
    return {
        "id_venda": venda_id,
        "CLIENTE_id_cliente": 1,
        "CAIXA_id_caixa": 2,
        "data_venda": datetime(2026, 7, 5, 9, 0),
        "valor_total": Decimal("0.00"),
        "status": "pendente",
        "forma_pagamento": "pix",
    }


def test_get_vendas_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(venda_router.venda_service, "listar_vendas", lambda _conn: [venda_response()])

    response = client.get("/vendas")

    assert response.status_code == 200
    assert response.json()[0]["id_venda"] == 1
    clear_overrides()


def test_get_venda_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, venda_id):
        assert venda_id == 1
        return venda_response()

    monkeypatch.setattr(venda_router.venda_service, "buscar_venda", fake_buscar)

    response = client.get("/vendas/1")

    assert response.status_code == 200
    assert response.json()["id_venda"] == 1
    clear_overrides()


def test_get_venda_por_id_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_buscar(_conn, _venda_id):
        raise HTTPException(status_code=404, detail="Venda nao encontrada")

    monkeypatch.setattr(venda_router.venda_service, "buscar_venda", fake_buscar)

    response = client.get("/vendas/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Venda nao encontrada"}
    clear_overrides()


def test_post_venda_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_criar(_conn, payload):
        assert payload.CLIENTE_id_cliente == 1
        assert not hasattr(payload, "valor_total")
        return venda_response()

    monkeypatch.setattr(venda_router.venda_service, "criar_venda", fake_criar)

    response = client.post(
        "/vendas",
        json={"CLIENTE_id_cliente": 1, "CAIXA_id_caixa": 2, "forma_pagamento": "pix"},
    )

    assert response.status_code == 201
    assert response.json()["valor_total"] == "0.00"
    clear_overrides()


def test_post_venda_rejeita_valor_total_do_cliente(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/vendas",
        json={"CLIENTE_id_cliente": 1, "CAIXA_id_caixa": 2, "valor_total": "999.00"},
    )

    assert response.status_code == 422
    clear_overrides()


def test_patch_status_venda_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_status(_conn, venda_id, payload):
        assert venda_id == 1
        assert payload.status == "concluida"
        return venda_response() | {"status": "concluida"}

    monkeypatch.setattr(venda_router.venda_service, "atualizar_status_venda", fake_status)

    response = client.patch("/vendas/1/status", json={"status": "concluida"})

    assert response.status_code == 200
    assert response.json()["status"] == "concluida"
    clear_overrides()


def test_patch_status_venda_rejeita_status_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.patch("/vendas/1/status", json={"status": "finalizada"})

    assert response.status_code == 422
    clear_overrides()


def test_patch_status_venda_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_status(_conn, _venda_id, _payload):
        raise HTTPException(status_code=404, detail="Venda nao encontrada")

    monkeypatch.setattr(venda_router.venda_service, "atualizar_status_venda", fake_status)

    response = client.patch("/vendas/404/status", json={"status": "cancelada"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Venda nao encontrada"}
    clear_overrides()


def test_delete_venda_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    deleted_ids = []
    monkeypatch.setattr(
        venda_router.venda_service,
        "deletar_venda",
        lambda _conn, venda_id: deleted_ids.append(venda_id),
    )

    response = client.delete("/vendas/1")

    assert response.status_code == 204
    assert response.content == b""
    assert deleted_ids == [1]
    clear_overrides()


def test_delete_venda_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_deletar(_conn, _venda_id):
        raise HTTPException(status_code=404, detail="Venda nao encontrada")

    monkeypatch.setattr(venda_router.venda_service, "deletar_venda", fake_deletar)

    response = client.delete("/vendas/404")

    assert response.status_code == 404
    assert response.json() == {"detail": "Venda nao encontrada"}
    clear_overrides()


def test_venda_router_nao_contem_sql():
    source = inspect.getsource(venda_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
