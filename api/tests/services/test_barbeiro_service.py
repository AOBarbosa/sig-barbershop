import pytest
from fastapi import HTTPException

from app.schemas.barbeiro_schema import BarbeiroCreate, BarbeiroUpdate
from app.services import barbeiro_service


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


def barb_row(barb_id=1):
    return {
        "id_barbeiro": barb_id,
        "PESSOA_id_pessoa": 1,
        "especialidade": "Corte",
        "ativo": True,
    }


def test_listar_barbeiros(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "listar", lambda _c: [barb_row()]
    )

    assert barbeiro_service.listar_barbeiros(conn) == [barb_row()]
    assert conn.started is False


def test_buscar_barbeiro_existente(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: barb_row()
    )

    assert barbeiro_service.buscar_barbeiro(conn, 1) == barb_row()


def test_buscar_barbeiro_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: None
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.buscar_barbeiro(conn, 404)

    assert exc.value.status_code == 404


def test_criar_barbeiro_controla_transacao(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: None
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "criar", lambda _c, _d: barb_row()
    )

    result = barbeiro_service.criar_barbeiro(
        conn, BarbeiroCreate(PESSOA_id_pessoa=1, especialidade="Corte", ativo=True)
    )

    assert result == barb_row()
    assert conn.committed is True


def test_criar_barbeiro_sem_pessoa_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(barbeiro_service.pessoa_repository, "buscar_por_id", lambda _c, _i: None)

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.criar_barbeiro(conn, BarbeiroCreate(PESSOA_id_pessoa=999))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_criar_barbeiro_duplicado_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.pessoa_repository, "buscar_por_id", lambda _c, _i: {"id_pessoa": 1}
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_pessoa", lambda _c, _i: barb_row()
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.criar_barbeiro(conn, BarbeiroCreate(PESSOA_id_pessoa=1))

    assert exc.value.status_code == 409
    assert conn.rolled_back is True


def test_atualizar_barbeiro_existente(monkeypatch):
    conn = FakeConn()
    novo = barb_row() | {"especialidade": "Degradê"}
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: barb_row()
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "atualizar", lambda _c, _i, _d: novo
    )

    result = barbeiro_service.atualizar_barbeiro(
        conn, 1, BarbeiroUpdate(especialidade="Degradê")
    )

    assert result == novo
    assert conn.committed is True


def test_atualizar_barbeiro_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: None
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.atualizar_barbeiro(conn, 404, BarbeiroUpdate(ativo=False))

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_barbeiro_sem_vinculo(monkeypatch):
    conn = FakeConn()
    called = []
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: barb_row()
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "existe_atendimento_vinculado", lambda _c, _i: False
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "deletar", lambda _c, i: called.append(i)
    )

    barbeiro_service.deletar_barbeiro(conn, 1)

    assert called == [1]
    assert conn.committed is True


def test_deletar_barbeiro_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: None
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.deletar_barbeiro(conn, 404)

    assert exc.value.status_code == 404
    assert conn.rolled_back is True


def test_deletar_barbeiro_com_atendimento_retorna_409(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "buscar_por_id", lambda _c, _i: barb_row()
    )
    monkeypatch.setattr(
        barbeiro_service.barbeiro_repository, "existe_atendimento_vinculado", lambda _c, _i: True
    )

    with pytest.raises(HTTPException) as exc:
        barbeiro_service.deletar_barbeiro(conn, 1)

    assert exc.value.status_code == 409
    assert conn.rolled_back is True
