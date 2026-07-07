from datetime import date, datetime

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import barbeiro_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def _pessoa_row():
    return {
        "id_pessoa": 1,
        "nome": "Pedro",
        "cpf": "55566677788",
        "email": "p@ex.com",
        "data_nascimento": date(1988, 11, 3),
        "created_at": datetime(2026, 7, 1, 10, 0, 0),
        "updated_at": datetime(2026, 7, 1, 10, 0, 0),
    }


def _barbeiro_row():
    return {
        "id_barbeiro": 1,
        "PESSOA_id_pessoa": 1,
        "especialidade": "Corte",
        "ativo": True,
    }


def test_post_barbeiro_completo_cria_pessoa_e_barbeiro(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.nome == "Pedro"
        assert payload.especialidade == "Corte"
        assert payload.ativo is True
        return {"barbeiro": _barbeiro_row(), "pessoa": _pessoa_row()}

    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "criar_barbeiro_completo", fake
    )

    response = client.post(
        "/barbeiros/completo",
        json={
            "nome": "Pedro",
            "cpf": "55566677788",
            "email": "p@ex.com",
            "data_nascimento": "1988-11-03",
            "especialidade": "Corte",
            "ativo": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["barbeiro"]["id_barbeiro"] == 1
    assert body["pessoa"]["nome"] == "Pedro"
    clear_overrides()


def test_post_barbeiro_completo_rejeita_cpf_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/barbeiros/completo",
        json={"nome": "X", "cpf": "abc"},
    )

    assert response.status_code == 422
    clear_overrides()


def test_post_barbeiro_completo_repassa_409_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")

    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "criar_barbeiro_completo", fake
    )

    response = client.post(
        "/barbeiros/completo",
        json={"nome": "X", "cpf": "12345678901"},
    )

    assert response.status_code == 409
    clear_overrides()


def test_post_barbeiro_completo_ativo_default_true(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    capturado = {}

    def fake(_c, payload):
        capturado["ativo"] = payload.ativo
        capturado["especialidade"] = payload.especialidade
        return {"barbeiro": _barbeiro_row(), "pessoa": _pessoa_row()}

    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "criar_barbeiro_completo", fake
    )

    response = client.post(
        "/barbeiros/completo",
        json={"nome": "Rafael", "cpf": "66677788899"},
    )

    assert response.status_code == 201
    assert capturado["ativo"] is True
    assert capturado["especialidade"] is None
    clear_overrides()
