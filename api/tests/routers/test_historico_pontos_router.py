from datetime import datetime
import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import historico_pontos_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def historico_response():
    return {
        "id_movimentacao": 1,
        "CLIENTE_PESSOA_id_pessoa": 1,
        "VENDA_id_venda": 1,
        "FIDELIDADE_id_fidelidade": 1,
        "pontos": 10,
        "tipo_movimentacao": "ACUMULA",
        "data_movimentacao": datetime(2026, 7, 5, 9, 0),
    }


def test_get_saldo_pontos_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        historico_pontos_router.historico_pontos_service,
        "buscar_saldo_pontos",
        lambda _conn, cliente_id: {"CLIENTE_PESSOA_id_pessoa": cliente_id, "saldo": 25},
    )

    response = client.get("/clientes/1/pontos")

    assert response.status_code == 200
    assert response.json() == {"CLIENTE_PESSOA_id_pessoa": 1, "saldo": 25}
    clear_overrides()


def test_get_saldo_pontos_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_saldo(_conn, _cliente_id):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    monkeypatch.setattr(historico_pontos_router.historico_pontos_service, "buscar_saldo_pontos", fake_saldo)

    response = client.get("/clientes/404/pontos")

    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente nao encontrado"}
    clear_overrides()


def test_get_historico_pontos_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        historico_pontos_router.historico_pontos_service,
        "listar_historico_pontos",
        lambda _conn, _cliente_id: [historico_response()],
    )

    response = client.get("/clientes/1/pontos/historico")

    assert response.status_code == 200
    assert response.json()[0]["id_movimentacao"] == 1
    clear_overrides()


def test_get_historico_pontos_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake_listar(_conn, _cliente_id):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    monkeypatch.setattr(historico_pontos_router.historico_pontos_service, "listar_historico_pontos", fake_listar)

    response = client.get("/clientes/404/pontos/historico")

    assert response.status_code == 404
    clear_overrides()


def test_historico_pontos_router_nao_contem_sql():
    source = inspect.getsource(historico_pontos_router)

    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
