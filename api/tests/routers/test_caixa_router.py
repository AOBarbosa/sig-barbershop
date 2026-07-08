import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import caixa_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def caixa_row(caixa_id=1):
    return {"PESSOA_id_pessoa": caixa_id}


def test_get_caixas(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        caixa_router.caixa_service, "listar_caixas", lambda _c: [caixa_row()]
    )

    response = client.get("/caixas")
    assert response.status_code == 200
    assert response.json() == [caixa_row()]
    clear_overrides()


def test_get_caixa_por_id(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(caixa_router.caixa_service, "buscar_caixa", lambda _c, i: caixa_row(i))

    response = client.get("/caixas/1")
    assert response.status_code == 200
    clear_overrides()


def test_get_caixa_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Caixa nao encontrado")

    monkeypatch.setattr(caixa_router.caixa_service, "buscar_caixa", fake)

    response = client.get("/caixas/404")
    assert response.status_code == 404
    clear_overrides()


def test_post_caixa_valida_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.PESSOA_id_pessoa == 1
        return caixa_row()

    monkeypatch.setattr(caixa_router.caixa_service, "criar_caixa", fake)

    response = client.post("/caixas", json={"PESSOA_id_pessoa": 1})
    assert response.status_code == 201
    clear_overrides()


def test_post_caixa_rejeita_pessoa_invalida(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post("/caixas", json={"PESSOA_id_pessoa": 0})
    assert response.status_code == 422
    clear_overrides()


def test_post_caixa_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como caixa")

    monkeypatch.setattr(caixa_router.caixa_service, "criar_caixa", fake)

    response = client.post("/caixas", json={"PESSOA_id_pessoa": 1})
    assert response.status_code == 409
    clear_overrides()


def test_delete_caixa_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    called = []
    monkeypatch.setattr(
        caixa_router.caixa_service, "deletar_caixa", lambda _c, i: called.append(i)
    )

    response = client.delete("/caixas/1")
    assert response.status_code == 204
    assert called == [1]
    clear_overrides()


def test_delete_caixa_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=409, detail="Caixa possui vendas")

    monkeypatch.setattr(caixa_router.caixa_service, "deletar_caixa", fake)

    response = client.delete("/caixas/1")
    assert response.status_code == 409
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(caixa_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
