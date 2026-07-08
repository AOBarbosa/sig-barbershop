import pytest
from fastapi import HTTPException

from app import dependencies


class FakeConn:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeRequest:
    def __init__(self, cookies=None):
        self.cookies = cookies or {}


def test_get_db_entrega_conexao_e_fecha_no_finally(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(dependencies, "get_connection", lambda: conn)

    generator = dependencies.get_db()
    yielded = next(generator)

    assert yielded is conn

    try:
        next(generator)
    except StopIteration:
        pass

    assert conn.closed is True


def test_get_current_user_le_cookie_e_delega_para_auth_service(monkeypatch):
    request = FakeRequest(cookies={"access_token": "token-fake"})
    usuario = {"id_pessoa": 1, "nome": "X", "email": "x@ex.com", "role": "admin"}

    def fake(_c, token):
        assert token == "token-fake"
        return usuario

    monkeypatch.setattr(dependencies.auth_service, "obter_usuario_atual", fake)

    assert dependencies.get_current_user(request, conn=object()) == usuario


def test_get_current_user_sem_cookie_repassa_401(monkeypatch):
    request = FakeRequest(cookies={})

    def fake(_c, token):
        assert token is None
        raise HTTPException(status_code=401, detail="Nao autenticado")

    monkeypatch.setattr(dependencies.auth_service, "obter_usuario_atual", fake)

    with pytest.raises(HTTPException) as exc:
        dependencies.get_current_user(request, conn=object())

    assert exc.value.status_code == 401


def test_get_current_user_opcional_sem_cookie_retorna_none():
    request = FakeRequest(cookies={})

    assert dependencies.get_current_user_opcional(request, conn=object()) is None


def test_get_current_user_opcional_com_token_invalido_retorna_none(monkeypatch):
    request = FakeRequest(cookies={"access_token": "invalido"})

    def fake(_c, _t):
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

    monkeypatch.setattr(dependencies.auth_service, "obter_usuario_atual", fake)

    assert dependencies.get_current_user_opcional(request, conn=object()) is None


def test_get_current_user_opcional_com_token_valido_retorna_usuario(monkeypatch):
    request = FakeRequest(cookies={"access_token": "token-fake"})
    usuario = {"id_pessoa": 1, "nome": "X", "email": "x@ex.com", "role": "admin"}
    monkeypatch.setattr(dependencies.auth_service, "obter_usuario_atual", lambda _c, _t: usuario)

    assert dependencies.get_current_user_opcional(request, conn=object()) == usuario


def test_require_admin_aceita_usuario_admin():
    usuario = {"role": "admin"}
    assert dependencies.require_admin(usuario) == usuario


def test_require_admin_rejeita_usuario_nao_admin():
    with pytest.raises(HTTPException) as exc:
        dependencies.require_admin({"role": "funcionario"})

    assert exc.value.status_code == 403


def test_require_funcionario_aceita_admin_e_funcionario():
    assert dependencies.require_funcionario({"role": "admin"})["role"] == "admin"
    assert dependencies.require_funcionario({"role": "funcionario"})["role"] == "funcionario"


def test_require_funcionario_rejeita_cliente():
    with pytest.raises(HTTPException) as exc:
        dependencies.require_funcionario({"role": "cliente"})

    assert exc.value.status_code == 403


def test_require_cliente_aceita_cliente():
    usuario = {"role": "cliente"}
    assert dependencies.require_cliente(usuario) == usuario


def test_require_cliente_rejeita_funcionario():
    with pytest.raises(HTTPException) as exc:
        dependencies.require_cliente({"role": "funcionario"})

    assert exc.value.status_code == 403
