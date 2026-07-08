import inspect

from fastapi import HTTPException

from app.core.security import COOKIE_NAME
from app.dependencies import get_db
from app.main import app
from app.routers import auth_router


class FakeConn:
    pass


def override_db():
    yield FakeConn()


def clear_overrides():
    app.dependency_overrides.clear()


def usuario_admin():
    return {"id_pessoa": 1, "nome": "Admin", "email": "admin@ex.com", "role": "admin"}


def test_login_sucesso_seta_cookie_httponly(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        auth_router.auth_service, "login", lambda _c, _p: ("token-fake", usuario_admin())
    )

    response = client.post("/auth/login", json={"email": "admin@ex.com", "senha": "admin123"})

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    assert response.cookies.get(COOKIE_NAME) == "token-fake"
    clear_overrides()


def test_login_credenciais_invalidas_repassa_401(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    monkeypatch.setattr(auth_router.auth_service, "login", fake)

    response = client.post("/auth/login", json={"email": "x@ex.com", "senha": "errada"})

    assert response.status_code == 401
    clear_overrides()


def test_registrar_cliente_sucesso_retorna_201_e_seta_cookie(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    usuario = {"id_pessoa": 5, "nome": "Novo", "email": "novo@ex.com", "role": "cliente"}
    monkeypatch.setattr(
        auth_router.auth_service, "registrar_cliente", lambda _c, _p: ("token-cliente", usuario)
    )

    response = client.post(
        "/auth/registrar-cliente",
        json={
            "nome": "Novo",
            "cpf": "12345678901",
            "email": "novo@ex.com",
            "senha": "senha123",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "cliente"
    assert response.cookies.get(COOKIE_NAME) == "token-cliente"
    clear_overrides()


def test_registrar_cliente_email_duplicado_repassa_409(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, _p):
        raise HTTPException(status_code=409, detail="Email ja cadastrado")

    monkeypatch.setattr(auth_router.auth_service, "registrar_cliente", fake)

    response = client.post(
        "/auth/registrar-cliente",
        json={"nome": "X", "email": "x@ex.com", "senha": "senha123"},
    )

    assert response.status_code == 409
    clear_overrides()


def test_logout_limpa_cookie(client):
    app.dependency_overrides[get_db] = override_db
    client.cookies.set(COOKIE_NAME, "token-fake")

    response = client.post("/auth/logout")

    assert response.status_code == 204
    set_cookie = response.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie
    assert "Max-Age=0" in set_cookie
    clear_overrides()


def test_me_com_cookie_valido_retorna_usuario(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        auth_router.auth_service, "obter_usuario_atual", lambda _c, token: usuario_admin()
    )
    client.cookies.set(COOKIE_NAME, "token-fake")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
    clear_overrides()
    client.cookies.delete(COOKIE_NAME)


def test_me_sem_cookie_repassa_401(client, monkeypatch):
    app.dependency_overrides[get_db] = override_db

    def fake(_c, token):
        assert token is None
        raise HTTPException(status_code=401, detail="Nao autenticado")

    monkeypatch.setattr(auth_router.auth_service, "obter_usuario_atual", fake)

    response = client.get("/auth/me")

    assert response.status_code == 401
    clear_overrides()


def test_router_nao_contem_sql():
    source = inspect.getsource(auth_router)
    assert "SELECT " not in source
    assert "INSERT " not in source
    assert "UPDATE " not in source
    assert "DELETE " not in source
