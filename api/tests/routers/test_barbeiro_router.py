import inspect

from fastapi import HTTPException

from app.dependencies import get_current_user_opcional, get_db, require_admin
from app.main import app
from app.routers import barbeiro_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def _usuario_admin():
    return {"id_pessoa": 1, "nome": "Admin", "email": "admin@ex.com", "role": "admin"}


def _override_admin_opcional():
    app.dependency_overrides.update(
        {get_db: override_db, get_current_user_opcional: _usuario_admin}
    )


def _override_admin():
    app.dependency_overrides.update({get_db: override_db, require_admin: _usuario_admin})


def barb_row(barb_id=1):
    return {
        "PESSOA_id_pessoa": 1,
        "apelido": "Corte",
        "comissao_percentual": 10.0,
    }


def test_get_barbeiros(client, monkeypatch):
    _override_admin_opcional()
    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "listar_barbeiros", lambda _c: [barb_row()]
    )

    response = client.get("/barbeiros")
    assert response.status_code == 200
    assert response.json() == [barb_row()]
    clear_overrides()


def test_get_barbeiro_por_id(client, monkeypatch):
    _override_admin_opcional()
    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "buscar_barbeiro", lambda _c, i: barb_row(i)
    )

    response = client.get("/barbeiros/1")
    assert response.status_code == 200
    clear_overrides()


def test_get_barbeiro_repassa_404(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _i):
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

    monkeypatch.setattr(barbeiro_router.barbeiro_service, "buscar_barbeiro", fake)

    response = client.get("/barbeiros/404")
    assert response.status_code == 404
    clear_overrides()


def test_get_disponibilidades_do_barbeiro_delega(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    disps = [
        {
            "id_disponibilidade": 1,
            "BARBEIRO_PESSOA_id_pessoa": 1,
            "dia_semana": "SEGUNDA",
            "hora_inicio": "09:00:00",
            "hora_fim": "18:00:00",
            "ativo": True,
        }
    ]

    def fake(_c, barbeiro_id):
        assert barbeiro_id == 1
        return disps

    monkeypatch.setattr(
        barbeiro_router.disponibilidade_service, "listar_por_barbeiro", fake
    )

    response = client.get("/barbeiros/1/disponibilidades")
    assert response.status_code == 200
    assert response.json() == disps
    clear_overrides()


def test_get_horarios_ocupados_do_barbeiro_e_publico(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, barbeiro_id, inicio, fim):
        assert barbeiro_id == 1
        assert inicio.isoformat() == "2026-07-13T00:00:00"
        assert fim.isoformat() == "2026-07-27T23:59:59"
        return [{"data_hora_inicio": "2026-07-13T14:30:00"}]

    monkeypatch.setattr(barbeiro_router.agenda_service, "listar_horarios_ocupados", fake)

    response = client.get(
        "/barbeiros/1/horarios-ocupados"
        "?inicio=2026-07-13T00:00:00&fim=2026-07-27T23:59:59"
    )

    assert response.status_code == 200
    assert response.json() == [{"data_hora_inicio": "2026-07-13T14:30:00"}]
    clear_overrides()


def test_post_barbeiro_valida_e_retorna_201(client, monkeypatch):
    _override_admin()

    def fake(_c, payload):
        assert payload.PESSOA_id_pessoa == 1
        assert payload.apelido == "Corte"
        return barb_row()

    monkeypatch.setattr(barbeiro_router.barbeiro_service, "criar_barbeiro", fake)

    response = client.post(
        "/barbeiros",
        json={"PESSOA_id_pessoa": 1, "apelido": "Corte", "comissao_percentual": 10.0},
    )
    assert response.status_code == 201
    clear_overrides()


def test_post_barbeiro_repassa_409(client, monkeypatch):
    _override_admin()

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como barbeiro")

    monkeypatch.setattr(barbeiro_router.barbeiro_service, "criar_barbeiro", fake)

    response = client.post("/barbeiros", json={"PESSOA_id_pessoa": 1})
    assert response.status_code == 409
    clear_overrides()


def test_put_barbeiro_delega(client, monkeypatch):
    _override_admin()

    def fake(_c, barb_id, payload):
        assert barb_id == 1
        assert payload.comissao_percentual == 5.0
        return barb_row() | {"comissao_percentual": 5.0}

    monkeypatch.setattr(barbeiro_router.barbeiro_service, "atualizar_barbeiro", fake)

    response = client.put("/barbeiros/1", json={"comissao_percentual": 5.0})
    assert response.status_code == 200
    assert response.json()["comissao_percentual"] == 5.0
    clear_overrides()


def test_delete_barbeiro_retorna_204(client, monkeypatch):
    _override_admin()
    called = []
    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "deletar_barbeiro", lambda _c, i: called.append(i)
    )

    response = client.delete("/barbeiros/1")
    assert response.status_code == 204
    assert called == [1]
    clear_overrides()


def test_delete_barbeiro_repassa_409(client, monkeypatch):
    _override_admin()

    def fake(_c, _i):
        raise HTTPException(status_code=409, detail="Barbeiro possui atendimentos")

    monkeypatch.setattr(barbeiro_router.barbeiro_service, "deletar_barbeiro", fake)

    response = client.delete("/barbeiros/1")
    assert response.status_code == 409
    clear_overrides()


def test_get_barbeiros_sem_login_oculta_comissao(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        barbeiro_router.barbeiro_service, "listar_barbeiros", lambda _c: [barb_row()]
    )

    response = client.get("/barbeiros")

    assert response.status_code == 200
    assert response.json()[0]["comissao_percentual"] is None
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(barbeiro_router)
    for verb in ("SELECT ", "INSERT ", "UPDATE ", "DELETE "):
        assert verb not in source
