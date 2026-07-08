from datetime import date, datetime

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import cliente_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def _pessoa_row(pessoa_id=1):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": "12345678901",
        "email": "f@ex.com",
        "data_nascimento": date(1990, 1, 1),
        "admin": False,
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def _cliente_row(cli_id=1, pessoa_id=1):
    return {"PESSOA_id_pessoa": pessoa_id, "preferencias": None, "observacoes": None}


def test_post_cliente_completo_cria_pessoa_e_cliente(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.nome == "Fulano"
        assert payload.cpf == "12345678901"
        return {"cliente": _cliente_row(), "pessoa": _pessoa_row()}

    monkeypatch.setattr(cliente_router.cliente_service, "criar_cliente_completo", fake)

    response = client.post(
        "/clientes/completo",
        json={
            "nome": "Fulano",
            "cpf": "12345678901",
            "email": "f@ex.com",
            "data_nascimento": "1990-01-01",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["cliente"]["PESSOA_id_pessoa"] == 1
    assert body["pessoa"]["nome"] == "Fulano"
    clear_overrides()


def test_post_cliente_completo_rejeita_cpf_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/clientes/completo",
        json={"nome": "X", "cpf": "123456789012345", "email": None},
    )

    assert response.status_code == 422
    clear_overrides()


def test_post_cliente_completo_repassa_409_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")

    monkeypatch.setattr(cliente_router.cliente_service, "criar_cliente_completo", fake)

    response = client.post(
        "/clientes/completo",
        json={"nome": "X", "cpf": "12345678901"},
    )

    assert response.status_code == 409
    clear_overrides()
