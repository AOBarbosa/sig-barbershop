import inspect

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


def cli_row(cli_id=1):
    return {"id_cliente": cli_id, "PESSOA_id_pessoa": 1}


def test_get_clientes_delega(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        cliente_router.cliente_service, "listar_clientes", lambda _c: [cli_row()]
    )

    response = client.get("/clientes")
    assert response.status_code == 200
    assert response.json() == [cli_row()]
    clear_overrides()


def test_get_cliente_por_id_delega(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, cli_id):
        assert cli_id == 1
        return cli_row()

    monkeypatch.setattr(cliente_router.cliente_service, "buscar_cliente", fake)

    response = client.get("/clientes/1")
    assert response.status_code == 200
    assert response.json()["id_cliente"] == 1
    clear_overrides()


def test_get_cliente_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")

    monkeypatch.setattr(cliente_router.cliente_service, "buscar_cliente", fake)

    response = client.get("/clientes/404")
    assert response.status_code == 404
    clear_overrides()


def test_post_cliente_valida_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.PESSOA_id_pessoa == 1
        return cli_row()

    monkeypatch.setattr(cliente_router.cliente_service, "criar_cliente", fake)

    response = client.post("/clientes", json={"PESSOA_id_pessoa": 1})
    assert response.status_code == 201
    clear_overrides()


def test_post_cliente_rejeita_pessoa_invalida(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post("/clientes", json={"PESSOA_id_pessoa": 0})
    assert response.status_code == 422
    clear_overrides()


def test_post_cliente_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como cliente")

    monkeypatch.setattr(cliente_router.cliente_service, "criar_cliente", fake)

    response = client.post("/clientes", json={"PESSOA_id_pessoa": 1})
    assert response.status_code == 409
    clear_overrides()


def test_delete_cliente_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    called = []
    monkeypatch.setattr(
        cliente_router.cliente_service, "deletar_cliente", lambda _c, i: called.append(i)
    )

    response = client.delete("/clientes/1")
    assert response.status_code == 204
    assert response.content == b""
    assert called == [1]
    clear_overrides()


def test_delete_cliente_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=409, detail="Cliente possui atendimentos")

    monkeypatch.setattr(cliente_router.cliente_service, "deletar_cliente", fake)

    response = client.delete("/clientes/1")
    assert response.status_code == 409
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(cliente_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
