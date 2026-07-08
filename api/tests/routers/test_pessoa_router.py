from datetime import date
import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import pessoa_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def pessoa_response(pessoa_id=1):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": "12345678901",
        "email": "f@ex.com",
        "data_nascimento": "1990-01-01",
        "admin": False,
    }


def pessoa_row(pessoa_id=1):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "cpf": "12345678901",
        "email": "f@ex.com",
        "data_nascimento": date(1990, 1, 1),
        "admin": False,
    }


def test_get_pessoas_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(pessoa_router.pessoa_service, "listar_pessoas", lambda _c: [pessoa_row()])

    response = client.get("/pessoas")

    assert response.status_code == 200
    assert response.json() == [pessoa_response()]
    clear_overrides()


def test_get_pessoa_por_id_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, pessoa_id):
        assert pessoa_id == 1
        return pessoa_row()

    monkeypatch.setattr(pessoa_router.pessoa_service, "buscar_pessoa", fake)

    response = client.get("/pessoas/1")

    assert response.status_code == 200
    assert response.json()["id_pessoa"] == 1
    clear_overrides()


def test_get_pessoa_por_id_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

    monkeypatch.setattr(pessoa_router.pessoa_service, "buscar_pessoa", fake)

    response = client.get("/pessoas/404")

    assert response.status_code == 404
    clear_overrides()


def test_get_telefones_da_pessoa_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    tels = [{"PESSOA_id_pessoa": 1, "telefone": "84999999999"}]

    def fake(_c, pessoa_id):
        assert pessoa_id == 1
        return tels

    monkeypatch.setattr(pessoa_router.telefone_service, "listar_por_pessoa", fake)

    response = client.get("/pessoas/1/telefones")

    assert response.status_code == 200
    assert response.json() == tels
    clear_overrides()


def test_post_pessoas_valida_payload_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.nome == "Fulano"
        assert payload.cpf == "12345678901"
        return pessoa_row()

    monkeypatch.setattr(pessoa_router.pessoa_service, "criar_pessoa", fake)

    response = client.post(
        "/pessoas",
        json={
            "nome": "Fulano",
            "cpf": "12345678901",
            "email": "f@ex.com",
            "data_nascimento": "1990-01-01",
        },
    )

    assert response.status_code == 201
    clear_overrides()


def test_post_pessoas_rejeita_cpf_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/pessoas",
        json={"nome": "X", "cpf": "123456789012345", "email": None},
    )

    assert response.status_code == 422
    clear_overrides()


def test_post_pessoas_repassa_409_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")

    monkeypatch.setattr(pessoa_router.pessoa_service, "criar_pessoa", fake)

    response = client.post(
        "/pessoas",
        json={"nome": "X", "cpf": "12345678901"},
    )

    assert response.status_code == 409
    clear_overrides()


def test_put_pessoa_delega_para_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, pessoa_id, payload):
        assert pessoa_id == 1
        assert payload.nome == "Novo"
        return pessoa_row() | {"nome": "Novo"}

    monkeypatch.setattr(pessoa_router.pessoa_service, "atualizar_pessoa", fake)

    response = client.put("/pessoas/1", json={"nome": "Novo"})

    assert response.status_code == 200
    assert response.json()["nome"] == "Novo"
    clear_overrides()


def test_put_pessoa_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i, _p):
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

    monkeypatch.setattr(pessoa_router.pessoa_service, "atualizar_pessoa", fake)

    response = client.put("/pessoas/404", json={"nome": "X"})

    assert response.status_code == 404
    clear_overrides()


def test_delete_pessoa_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    called = []
    monkeypatch.setattr(
        pessoa_router.pessoa_service, "deletar_pessoa", lambda _c, i: called.append(i)
    )

    response = client.delete("/pessoas/1")

    assert response.status_code == 204
    assert response.content == b""
    assert called == [1]
    clear_overrides()


def test_delete_pessoa_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=409, detail="Pessoa possui vinculos")

    monkeypatch.setattr(pessoa_router.pessoa_service, "deletar_pessoa", fake)

    response = client.delete("/pessoas/1")

    assert response.status_code == 409
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(pessoa_router)
    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
