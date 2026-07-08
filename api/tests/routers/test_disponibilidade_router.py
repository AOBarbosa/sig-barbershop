import inspect

from fastapi import HTTPException

from app.dependencies import get_db
from app.main import app
from app.routers import disponibilidade_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def disp_row(disp_id=1):
    return {
        "id_disponibilidade": disp_id,
        "BARBEIRO_PESSOA_id_pessoa": 1,
        "dia_semana": "SEGUNDA",
        "hora_inicio": "09:00:00",
        "hora_fim": "18:00:00",
    }


def test_get_disponibilidade_por_id(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service,
        "buscar_disponibilidade",
        lambda _c, i: disp_row(i),
    )

    response = client.get("/disponibilidades/1")
    assert response.status_code == 200
    assert response.json()["id_disponibilidade"] == 1
    clear_overrides()


def test_get_disponibilidade_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Disponibilidade nao encontrada")

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "buscar_disponibilidade", fake
    )

    response = client.get("/disponibilidades/404")
    assert response.status_code == 404
    clear_overrides()


def test_post_disponibilidade_valida_e_retorna_201(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, payload):
        assert payload.BARBEIRO_PESSOA_id_pessoa == 1
        assert payload.dia_semana.value == "SEGUNDA"
        return disp_row()

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "criar_disponibilidade", fake
    )

    response = client.post(
        "/disponibilidades",
        json={
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "SEGUNDA",
            "hora_inicio": "09:00:00",
            "hora_fim": "18:00:00",
        },
    )
    assert response.status_code == 201
    clear_overrides()


def test_post_disponibilidade_rejeita_hora_fim_menor_ou_igual(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/disponibilidades",
        json={
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "SEGUNDA",
            "hora_inicio": "18:00:00",
            "hora_fim": "09:00:00",
        },
    )
    assert response.status_code == 422
    clear_overrides()


def test_post_disponibilidade_rejeita_dia_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.post(
        "/disponibilidades",
        json={
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "sabbatical",
            "hora_inicio": "09:00:00",
            "hora_fim": "18:00:00",
        },
    )
    assert response.status_code == 422
    clear_overrides()


def test_post_disponibilidade_repassa_404_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "criar_disponibilidade", fake
    )

    response = client.post(
        "/disponibilidades",
        json={
            "BARBEIRO_PESSOA_id_pessoa": 999,
            "dia_semana": "SEGUNDA",
            "hora_inicio": "09:00:00",
            "hora_fim": "18:00:00",
        },
    )
    assert response.status_code == 404
    clear_overrides()


def test_post_disponibilidade_repassa_409_do_service(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="Barbeiro ja possui disponibilidade")

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "criar_disponibilidade", fake
    )

    response = client.post(
        "/disponibilidades",
        json={
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "SEGUNDA",
            "hora_inicio": "09:00:00",
            "hora_fim": "18:00:00",
        },
    )
    assert response.status_code == 409
    clear_overrides()


def test_put_disponibilidade_delega(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, disp_id, payload):
        assert disp_id == 1
        assert payload.hora_fim.isoformat() == "19:00:00"
        return disp_row() | {"hora_fim": "19:00:00"}

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "atualizar_disponibilidade", fake
    )

    response = client.put("/disponibilidades/1", json={"hora_fim": "19:00:00"})
    assert response.status_code == 200
    assert response.json()["hora_fim"] == "19:00:00"
    clear_overrides()


def test_put_disponibilidade_rejeita_intervalo_invalido(client):
    app.dependency_overrides[get_db] = override_db

    response = client.put(
        "/disponibilidades/1",
        json={"hora_inicio": "18:00:00", "hora_fim": "09:00:00"},
    )
    assert response.status_code == 422
    clear_overrides()


def test_delete_disponibilidade_retorna_204(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    called = []
    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service,
        "deletar_disponibilidade",
        lambda _c, i: called.append(i),
    )

    response = client.delete("/disponibilidades/1")
    assert response.status_code == 204
    assert called == [1]
    clear_overrides()


def test_delete_disponibilidade_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Disponibilidade nao encontrada")

    monkeypatch.setattr(
        disponibilidade_router.disponibilidade_service, "deletar_disponibilidade", fake
    )

    response = client.delete("/disponibilidades/404")
    assert response.status_code == 404
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(disponibilidade_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
