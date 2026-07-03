import pytest
from fastapi import HTTPException

from app.schemas.fidelidade_schema import FidelidadeCreate, FidelidadeUpdate
from app.services import fidelidade_service


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


def test_listar_fidelidades_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [{"id_fidelidade": 1}]
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "listar", lambda received_conn: rows
    )

    result = fidelidade_service.listar_fidelidades(conn)

    assert result == rows
    assert conn.started is False


def test_buscar_fidelidade_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    fidelidade = {"id_fidelidade": 1}
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository,
        "buscar_por_id",
        lambda _conn, _id: fidelidade,
    )

    result = fidelidade_service.buscar_fidelidade(conn, 1)

    assert result == fidelidade
    assert conn.started is False


def test_buscar_fidelidade_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: None
    )

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.buscar_fidelidade(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_criar_fidelidade_com_apenas_servico_controla_transacao_e_retorna_registro(monkeypatch):
    conn = FakeConn()
    created = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "criar", lambda _conn, _data: created
    )

    result = fidelidade_service.criar_fidelidade(
        conn,
        FidelidadeCreate(SERVICO_id_servico=7, pontos=10),
    )

    assert result == created
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_fidelidade_com_apenas_produto_controla_transacao_e_retorna_registro(monkeypatch):
    conn = FakeConn()
    created = {"id_fidelidade": 1, "SERVICO_id_servico": None, "PRODUTO_id_produto": 5, "pontos": 10}

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "criar", lambda _conn, _data: created
    )

    result = fidelidade_service.criar_fidelidade(
        conn,
        FidelidadeCreate(PRODUTO_id_produto=5, pontos=10),
    )

    assert result == created
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_criar_fidelidade_com_ambos_faz_rollback_e_retorna_422(monkeypatch):
    conn = FakeConn()
    criado = False

    def fake_criar(_conn, _data):
        nonlocal criado
        criado = True

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "criar", fake_criar)

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.criar_fidelidade(
            conn,
            FidelidadeCreate(SERVICO_id_servico=7, PRODUTO_id_produto=5, pontos=10),
        )

    assert exc.value.status_code == 422
    assert criado is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_criar_fidelidade_sem_nenhum_faz_rollback_e_retorna_422(monkeypatch):
    conn = FakeConn()
    criado = False

    def fake_criar(_conn, _data):
        nonlocal criado
        criado = True

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "criar", fake_criar)

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.criar_fidelidade(
            conn,
            FidelidadeCreate(pontos=10),
        )

    assert exc.value.status_code == 422
    assert criado is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_criar_fidelidade_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()

    def fake_criar(_conn, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        fidelidade_service.criar_fidelidade(
            conn,
            FidelidadeCreate(SERVICO_id_servico=7, pontos=10),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_fidelidade_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: None
    )

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.atualizar_fidelidade(conn, 999, FidelidadeUpdate(pontos=20))

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_fidelidade_trocando_servico_por_produto_controla_transacao(monkeypatch):
    conn = FakeConn()
    atual = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}
    updated = {"id_fidelidade": 1, "SERVICO_id_servico": None, "PRODUTO_id_produto": 5, "pontos": 10}

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: atual
    )

    def fake_atualizar(received_conn, fidelidade_id, data):
        assert received_conn is conn
        assert fidelidade_id == 1
        assert data == {"SERVICO_id_servico": None, "PRODUTO_id_produto": 5}
        return updated

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "atualizar", fake_atualizar)

    result = fidelidade_service.atualizar_fidelidade(
        conn,
        1,
        FidelidadeUpdate(SERVICO_id_servico=None, PRODUTO_id_produto=5),
    )

    assert result == updated
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_fidelidade_so_pontos_mantem_referencia_atual_e_passa_na_xor(monkeypatch):
    conn = FakeConn()
    atual = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}
    updated = atual | {"pontos": 20}

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: atual
    )
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository,
        "atualizar",
        lambda _conn, _id, _data: updated,
    )

    result = fidelidade_service.atualizar_fidelidade(conn, 1, FidelidadeUpdate(pontos=20))

    assert result == updated
    assert conn.committed is True


def test_atualizar_fidelidade_definindo_ambos_faz_rollback_e_retorna_422(monkeypatch):
    conn = FakeConn()
    atual = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}
    atualizado = False

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: atual
    )

    def fake_atualizar(_conn, _id, _data):
        nonlocal atualizado
        atualizado = True

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "atualizar", fake_atualizar)

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.atualizar_fidelidade(
            conn, 1, FidelidadeUpdate(PRODUTO_id_produto=5)
        )

    assert exc.value.status_code == 422
    assert atualizado is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_fidelidade_removendo_referencia_unica_faz_rollback_e_retorna_422(monkeypatch):
    conn = FakeConn()
    atual = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}
    atualizado = False

    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: atual
    )

    def fake_atualizar(_conn, _id, _data):
        nonlocal atualizado
        atualizado = True

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "atualizar", fake_atualizar)

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.atualizar_fidelidade(
            conn, 1, FidelidadeUpdate(SERVICO_id_servico=None)
        )

    assert exc.value.status_code == 422
    assert atualizado is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_fidelidade_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    atual = {"id_fidelidade": 1, "SERVICO_id_servico": 7, "PRODUTO_id_produto": None, "pontos": 10}
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: atual
    )

    def fake_atualizar(_conn, _id, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "atualizar", fake_atualizar)

    with pytest.raises(RuntimeError):
        fidelidade_service.atualizar_fidelidade(conn, 1, FidelidadeUpdate(pontos=20))

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_fidelidade_existente_controla_transacao(monkeypatch):
    conn = FakeConn()
    deleted_ids = []
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_fidelidade": 1},
    )
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository,
        "deletar",
        lambda _conn, fidelidade_id: deleted_ids.append(fidelidade_id),
    )

    result = fidelidade_service.deletar_fidelidade(conn, 1)

    assert result is None
    assert deleted_ids == [1]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_deletar_fidelidade_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository, "buscar_por_id", lambda _conn, _id: None
    )

    with pytest.raises(HTTPException) as exc:
        fidelidade_service.deletar_fidelidade(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_fidelidade_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        fidelidade_service.fidelidade_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_fidelidade": 1},
    )

    def fake_deletar(_conn, _fidelidade_id):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(fidelidade_service.fidelidade_repository, "deletar", fake_deletar)

    with pytest.raises(RuntimeError):
        fidelidade_service.deletar_fidelidade(conn, 1)

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True
