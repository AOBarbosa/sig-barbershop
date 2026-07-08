import pytest
from fastapi import HTTPException

from app.core.security import criar_token, hash_senha
from app.schemas.auth_schema import LoginRequest, RegistroClienteRequest
from app.services import auth_service


class FakeConn:
    def __init__(self):
        self.started = False
        self.committed = False
        self.rolled_back = False

    def start_transaction(self):
        self.started = True

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


def pessoa_row(pessoa_id=1, admin=False, senha="senha123"):
    return {
        "id_pessoa": pessoa_id,
        "nome": "Fulano",
        "email": "fulano@ex.com",
        "cpf": "12345678901",
        "admin": admin,
        "senha_hash": hash_senha(senha) if senha else None,
    }


def _sem_vinculos(monkeypatch):
    monkeypatch.setattr(auth_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(auth_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(auth_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: None)


def test_login_admin_com_credenciais_corretas_retorna_token_e_role_admin(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(admin=True, senha="admin123")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)
    _sem_vinculos(monkeypatch)

    token, usuario = auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="admin123"))

    assert usuario["role"] == "admin"
    assert usuario["id_pessoa"] == 1
    assert isinstance(token, str) and token


def test_login_funcionario_via_barbeiro_retorna_role_funcionario(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(admin=False, senha="func123")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)
    monkeypatch.setattr(
        auth_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: {"PESSOA_id_pessoa": 1}
    )
    monkeypatch.setattr(auth_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(auth_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: None)

    _, usuario = auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="func123"))

    assert usuario["role"] == "funcionario"


def test_login_funcionario_via_caixa_retorna_role_funcionario(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(admin=False, senha="caixa123")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)
    monkeypatch.setattr(auth_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(
        auth_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: {"PESSOA_id_pessoa": 1}
    )
    monkeypatch.setattr(auth_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: None)

    _, usuario = auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="caixa123"))

    assert usuario["role"] == "funcionario"


def test_login_cliente_retorna_role_cliente(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(admin=False, senha="cliente123")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)
    monkeypatch.setattr(auth_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(auth_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: None)
    monkeypatch.setattr(
        auth_service.cliente_repository, "buscar_por_pessoa", lambda _c, _i: {"PESSOA_id_pessoa": 1}
    )

    _, usuario = auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="cliente123"))

    assert usuario["role"] == "cliente"


def test_login_pessoa_sem_papel_lanca_403(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(admin=False, senha="semrole123")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)
    _sem_vinculos(monkeypatch)

    with pytest.raises(HTTPException) as exc:
        auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="semrole123"))

    assert exc.value.status_code == 403


def test_login_senha_incorreta_lanca_401(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(senha="senhacerta")
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)

    with pytest.raises(HTTPException) as exc:
        auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="senhaerrada"))

    assert exc.value.status_code == 401


def test_login_email_inexistente_lanca_401(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: None)

    with pytest.raises(HTTPException) as exc:
        auth_service.login(conn, LoginRequest(email="naoexiste@ex.com", senha="qualquer"))

    assert exc.value.status_code == 401


def test_login_pessoa_sem_senha_definida_lanca_401(monkeypatch):
    conn = FakeConn()
    pessoa = pessoa_row(senha=None)
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _e: pessoa)

    with pytest.raises(HTTPException) as exc:
        auth_service.login(conn, LoginRequest(email="fulano@ex.com", senha="qualquer"))

    assert exc.value.status_code == 401


def _registro_payload():
    return RegistroClienteRequest(
        nome="Novo Cliente",
        cpf="99988877766",
        email="novo@ex.com",
        senha="senha123",
    )


def test_registrar_cliente_cria_pessoa_e_cliente_e_retorna_token(monkeypatch):
    conn = FakeConn()
    criado = {"id_pessoa": 42, "nome": "Novo Cliente", "email": "novo@ex.com"}

    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_email", lambda _c, _v: None)
    monkeypatch.setattr(auth_service.pessoa_repository, "criar", lambda _c, _d: criado)
    senha_atualizada = {}
    monkeypatch.setattr(
        auth_service.pessoa_repository,
        "atualizar_senha",
        lambda _c, pid, h: senha_atualizada.update(id=pid, hash=h),
    )
    cliente_criado = {}
    monkeypatch.setattr(
        auth_service.cliente_repository, "criar", lambda _c, d: cliente_criado.update(d)
    )

    token, usuario = auth_service.registrar_cliente(conn, _registro_payload())

    assert usuario["role"] == "cliente"
    assert usuario["id_pessoa"] == 42
    assert isinstance(token, str) and token
    assert senha_atualizada["id"] == 42
    assert cliente_criado["PESSOA_id_pessoa"] == 42
    assert conn.committed is True
    assert conn.rolled_back is False


def test_registrar_cliente_cpf_duplicado_lanca_409_e_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        auth_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: {"id_pessoa": 1}
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.registrar_cliente(conn, _registro_payload())

    assert exc.value.status_code == 409
    assert conn.rolled_back is True
    assert conn.committed is False


def test_registrar_cliente_email_duplicado_lanca_409_e_faz_rollback(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_cpf", lambda _c, _v: None)
    monkeypatch.setattr(
        auth_service.pessoa_repository, "buscar_por_email", lambda _c, _v: {"id_pessoa": 1}
    )

    with pytest.raises(HTTPException) as exc:
        auth_service.registrar_cliente(conn, _registro_payload())

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_obter_usuario_atual_sem_token_lanca_401():
    conn = FakeConn()

    with pytest.raises(HTTPException) as exc:
        auth_service.obter_usuario_atual(conn, None)

    assert exc.value.status_code == 401


def test_obter_usuario_atual_com_token_invalido_lanca_401():
    conn = FakeConn()

    with pytest.raises(HTTPException) as exc:
        auth_service.obter_usuario_atual(conn, "token-invalido")

    assert exc.value.status_code == 401


def test_obter_usuario_atual_pessoa_inexistente_lanca_401(monkeypatch):
    conn = FakeConn()
    token = criar_token({"sub": "999", "role": "admin"})
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        auth_service.obter_usuario_atual(conn, token)

    assert exc.value.status_code == 401


def test_obter_usuario_atual_retorna_usuario_com_role(monkeypatch):
    conn = FakeConn()
    token = criar_token({"sub": "1", "role": "admin"})
    pessoa = pessoa_row(admin=True)
    monkeypatch.setattr(auth_service.pessoa_repository, "buscar_por_id", lambda _c, _i: pessoa)

    usuario = auth_service.obter_usuario_atual(conn, token)

    assert usuario["role"] == "admin"
    assert usuario["id_pessoa"] == 1
