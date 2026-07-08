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
        "PESSOA_id_pessoa": 1,
        "apelido": "Corte",
        "comissao_percentual": 10.0,
    }


def test_post_barbeiro_completo_cria_pessoa_e_barbeiro(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.nome == "Pedro"
        assert payload.apelido == "Corte"
        assert payload.comissao_percentual == 10.0
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
            "apelido": "Corte",
            "comissao_percentual": 10.0,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["barbeiro"]["PESSOA_id_pessoa"] == 1
    assert body["pessoa"]["nome"] == "Pedro"
    clear_overrides()


def test_post_barbeiro_completo_rejeita_cpf_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/barbeiros/completo",
        json={"nome": "X", "cpf": "123456789012345"},
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


def test_post_barbeiro_completo_comissao_percentual_default_none(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    capturado = {}

    def fake(_c, payload):
        capturado["comissao_percentual"] = payload.comissao_percentual
        capturado["apelido"] = payload.apelido
        return {"barbeiro": _barbeiro_row(), "pessoa": _pessoa_row()}

    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "criar_barbeiro_completo", fake
    )

    response = client.post(
        "/barbeiros/completo",
        json={"nome": "Rafael", "cpf": "66677788899"},
    )

    assert response.status_code == 201
    assert capturado["comissao_percentual"] is None
    assert capturado["apelido"] is None
    clear_overrides()


def test_put_barbeiro_completo_atualiza_pessoa_e_barbeiro(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, barbeiro_id, payload):
        assert barbeiro_id == 1
        assert payload.nome == "Pedro Atualizado"
        assert payload.apelido == "Barba"
        assert payload.comissao_percentual == 5.0
        return {
            "barbeiro": _barbeiro_row() | {"apelido": "Barba", "comissao_percentual": 5.0},
            "pessoa": _pessoa_row() | {"nome": "Pedro Atualizado"},
        }

    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "atualizar_barbeiro_completo", fake
    )

    response = client.put(
        "/barbeiros/1/completo",
        json={
            "nome": "Pedro Atualizado",
            "cpf": "55566677788",
            "email": "p@ex.com",
            "data_nascimento": "1988-11-03",
            "apelido": "Barba",
            "comissao_percentual": 5.0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["barbeiro"]["apelido"] == "Barba"
    assert body["barbeiro"]["comissao_percentual"] == 5.0
    assert body["pessoa"]["nome"] == "Pedro Atualizado"
    clear_overrides()
