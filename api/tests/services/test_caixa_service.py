import pytest
from fastapi import HTTPException

from app.schemas.caixa_schema import CaixaCreate
from app.services import caixa_service


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


def caixa_row(caixa_id=1, pessoa_id=1):
    return {"id_caixa": caixa_id, "PESSOA_id_pessoa": pessoa_id}


def test_listar_caixas_sem_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(caixa_service.caixa_repository, "listar", lambda _c: [caixa_row()])

    assert caixa_service.listar_caixas(conn) == [caixa_row()]
    assert conn.started is False


def test_buscar_caixa_existente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        caixa_service.caixa_repository, "buscar_por_id", lambda _c, _i: caixa_row()
    )

    assert caixa_service.buscar_caixa(conn, 1) == caixa_row()


def test_buscar_caixa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(caixa_service.caixa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        caixa_service.buscar_caixa(conn, 404)

    assert exc.value.status_code == 404


def test_criar_caixa_controla_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        caixa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        caixa_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: None
    )
    monkeypatch.setattr(caixa_service.caixa_repository, "criar", lambda _c, _d: caixa_row())

    result = caixa_service.criar_caixa(conn, CaixaCreate(PESSOA_id_pessoa=1))

    assert result == caixa_row()
    assert conn.committed is True


def test_criar_caixa_sem_pessoa_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(caixa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        caixa_service.criar_caixa(conn, CaixaCreate(PESSOA_id_pessoa=999))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_criar_caixa_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        caixa_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        caixa_service.caixa_repository, "buscar_por_pessoa", lambda _c, _i: caixa_row()
    )

    with pytest.raises(HTTPException) as exc:
        caixa_service.criar_caixa(conn, CaixaCreate(PESSOA_id_pessoa=1))

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_deletar_caixa_sem_vinculo(monkeypatch):
    conn = FakeConn()
    called = []
    monkeypatch.setattr(
        caixa_service.caixa_repository, "buscar_por_id", lambda _c, _i: caixa_row()
    )
    monkeypatch.setattr(
        caixa_service.caixa_repository, "existe_venda_vinculada", lambda _c, _i: False
    )
    monkeypatch.setattr(
        caixa_service.caixa_repository, "deletar", lambda _c, i: called.append(i)
    )

    caixa_service.deletar_caixa(conn, 1)

    assert called == [1]
    assert conn.committed is True


def test_deletar_caixa_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(caixa_service.caixa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        caixa_service.deletar_caixa(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_caixa_com_venda_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        caixa_service.caixa_repository, "buscar_por_id", lambda _c, _i: caixa_row()
    )
    monkeypatch.setattr(
        caixa_service.caixa_repository, "existe_venda_vinculada", lambda _c, _i: True
    )

    with pytest.raises(HTTPException) as exc:
        caixa_service.deletar_caixa(conn, 1)

    assert exc.value.status_code == 409
    assert conn.rolled_back is True
