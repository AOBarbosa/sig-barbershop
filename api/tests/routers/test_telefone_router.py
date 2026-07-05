import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import telefone_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def tel_row(tel_id=1):
    return {"id_telefone": tel_id, "PESSOA_id_pessoa": 1, "numero": "84999999999"}


def test_get_telefone_por_id(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        telefone_router.telefone_service, "buscar_telefone", lambda _c, i: tel_row(i)
    )

    response = client.get("/telefones/1")

    assert response.status_code == 200
    assert response.json()["id_telefone"] == 1
    clear_overrides()


def test_get_telefone_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Telefone nao encontrado")

    monkeypatch.setattr(telefone_router.telefone_service, "buscar_telefone", fake)

    response = client.get("/telefones/404")
    assert response.status_code == 404
    clear_overrides()


def test_post_telefone_valida_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.PESSOA_id_pessoa == 1
        assert payload.numero == "84999999999"
        return tel_row()

    monkeypatch.setattr(telefone_router.telefone_service, "criar_telefone", fake)

    response = client.post(
        "/telefones", json={"PESSOA_id_pessoa": 1, "numero": "84999999999"}
    )

    assert response.status_code == 201
    clear_overrides()


def test_post_telefone_rejeita_numero_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post("/telefones", json={"PESSOA_id_pessoa": 1, "numero": "abc"})

    assert response.status_code == 422
    clear_overrides()


def test_post_telefone_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

    monkeypatch.setattr(telefone_router.telefone_service, "criar_telefone", fake)

    response = client.post(
        "/telefones", json={"PESSOA_id_pessoa": 999, "numero": "84999999999"}
    )

    assert response.status_code == 404
    clear_overrides()


def test_put_telefone_delega(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, tel_id, payload):
        assert tel_id == 1
        assert payload.numero == "84988888888"
        return tel_row() | {"numero": "84988888888"}

    monkeypatch.setattr(telefone_router.telefone_service, "atualizar_telefone", fake)

    response = client.put("/telefones/1", json={"numero": "84988888888"})

    assert response.status_code == 200
    assert response.json()["numero"] == "84988888888"
    clear_overrides()


def test_delete_telefone_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    called = []
    monkeypatch.setattr(
        telefone_router.telefone_service, "deletar_telefone", lambda _c, i: called.append(i)
    )

    response = client.delete("/telefones/1")

    assert response.status_code == 204
    assert response.content == b""
    assert called == [1]
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(telefone_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
