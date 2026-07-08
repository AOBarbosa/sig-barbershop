import inspect

from fastapi import HTTPException

from app.dependencies import get_db, require_funcionario
from app.main import app
from app.routers import telefone_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def _usuario_funcionario():
    return {"id_pessoa": 99, "nome": "Func", "email": "f@ex.com", "role": "funcionario"}


def _override_funcionario():
    app.dependency_overrides.update(
        {get_db: override_db, require_funcionario: _usuario_funcionario}
    )


def tel_row(pessoa_id=1, telefone="84999999999"):
    return {"PESSOA_id_pessoa": pessoa_id, "telefone": telefone}


def test_get_telefone_por_id(client, monkeypatch):
    _override_funcionario()
    monkeypatch.setattr(
        telefone_router.telefone_service,
        "buscar_telefone",
        lambda _c, pessoa_id, telefone: tel_row(pessoa_id, telefone),
    )

    response = client.get("/telefones/1/84999999999")

    assert response.status_code == 200
    assert response.json()["PESSOA_id_pessoa"] == 1
    clear_overrides()


def test_get_telefone_repassa_404(client, monkeypatch):
    _override_funcionario()

    def fake(_c, _pessoa_id, _telefone):
        raise HTTPException(status_code=404, detail="Telefone nao encontrado")

    monkeypatch.setattr(telefone_router.telefone_service, "buscar_telefone", fake)

    response = client.get("/telefones/404/84999999999")
    assert response.status_code == 404
    clear_overrides()


def test_post_telefone_valida_e_retorna_201(client, monkeypatch):
    _override_funcionario()

    def fake(_c, payload):
        assert payload.PESSOA_id_pessoa == 1
        assert payload.telefone == "84999999999"
        return tel_row()

    monkeypatch.setattr(telefone_router.telefone_service, "criar_telefone", fake)

    response = client.post(
        "/telefones", json={"PESSOA_id_pessoa": 1, "telefone": "84999999999"}
    )

    assert response.status_code == 201
    clear_overrides()


def test_post_telefone_rejeita_telefone_invalido(client):
    _override_funcionario()

    response = client.post("/telefones", json={"PESSOA_id_pessoa": 1, "telefone": ""})

    assert response.status_code == 422
    clear_overrides()


def test_post_telefone_repassa_404_do_service(client, monkeypatch):
    _override_funcionario()

    def fake(_c, _p):
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

    monkeypatch.setattr(telefone_router.telefone_service, "criar_telefone", fake)

    response = client.post(
        "/telefones", json={"PESSOA_id_pessoa": 999, "telefone": "84999999999"}
    )

    assert response.status_code == 404
    clear_overrides()


def test_put_telefone_delega(client, monkeypatch):
    _override_funcionario()

    def fake(_c, pessoa_id, telefone, payload):
        assert pessoa_id == 1
        assert telefone == "84999999999"
        assert payload.telefone == "84988888888"
        return tel_row(telefone="84988888888")

    monkeypatch.setattr(telefone_router.telefone_service, "atualizar_telefone", fake)

    response = client.put(
        "/telefones/1/84999999999", json={"telefone": "84988888888"}
    )

    assert response.status_code == 200
    assert response.json()["telefone"] == "84988888888"
    clear_overrides()


def test_delete_telefone_retorna_204(client, monkeypatch):
    _override_funcionario()
    called = []
    monkeypatch.setattr(
        telefone_router.telefone_service,
        "deletar_telefone",
        lambda _c, pessoa_id, telefone: called.append((pessoa_id, telefone)),
    )

    response = client.delete("/telefones/1/84999999999")

    assert response.status_code == 204
    assert response.content == b""
    assert called == [(1, "84999999999")]
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(telefone_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
