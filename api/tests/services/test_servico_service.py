import pytest
from fastapi import HTTPException

from app.schemas.servico_schema import ServicoCreate, ServicoUpdate
from app.services import servico_service


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


def test_criar_servico_controla_transacao_e_retorna_servico(monkeypatch):
    conn = FakeConn()
    created = {
        "id_servico": 1,
        "nome": "Corte",
        "ativo": True,
        "preco": 40.0,
        "duracao_em_minutos": 45,
        "pontos_gerados": 4,
    }
    historicos = []

    def fake_criar(received_conn, data):
        assert received_conn is conn
        assert data["nome"] == "Corte"
        assert "preco" not in data
        return {"id_servico": 1, "nome": "Corte", "ativo": True}

    def fake_criar_historico(received_conn, **kwargs):
        assert received_conn is conn
        historicos.append(kwargs)

    def fake_buscar(received_conn, servico_id):
        assert received_conn is conn
        assert servico_id == 1
        return created

    monkeypatch.setattr(servico_service.servico_repository, "criar", fake_criar)
    monkeypatch.setattr(servico_service.historico_servico_repository, "criar", fake_criar_historico)
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", fake_buscar)

    result = servico_service.criar_servico(
        conn,
        ServicoCreate(
            nome="Corte",
            ativo=True,
            preco=40,
            duracao_em_minutos=45,
            pontos_gerados=4,
        ),
    )

    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False
    assert historicos == [
        {
            "servico_id": 1,
            "preco": 40,
            "duracao_em_minutos": 45,
            "pontos_gerados": 4,
            "ativo": True,
        }
    ]
    assert result == created


def test_listar_servicos_retorna_repository_sem_transacao(monkeypatch):
    conn = FakeConn()
    rows = [{"id_servico": 1}]
    monkeypatch.setattr(servico_service.servico_repository, "listar", lambda received_conn: rows)

    result = servico_service.listar_servicos(conn)

    assert result == rows
    assert conn.started is False
    assert conn.committed is False
    assert conn.rolled_back is False


def test_buscar_servico_existente_retorna_registro(monkeypatch):
    conn = FakeConn()
    servico = {"id_servico": 1, "nome": "Corte"}
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda received_conn, servico_id: servico,
    )

    result = servico_service.buscar_servico(conn, 1)

    assert result == servico
    assert conn.started is False


def test_buscar_servico_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        servico_service.buscar_servico(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_criar_servico_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()

    def fake_criar(_conn, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(servico_service.servico_repository, "criar", fake_criar)

    with pytest.raises(RuntimeError):
        servico_service.criar_servico(
            conn,
            ServicoCreate(
                nome="Corte",
                ativo=True,
                preco=40,
                duracao_em_minutos=45,
                pontos_gerados=4,
            ),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_servico_existente_controla_transacao_e_retorna_servico(monkeypatch):
    conn = FakeConn()
    current = {
        "id_servico": 1,
        "nome": "Corte",
        "ativo": True,
    }
    updated = {
        "id_servico": 1,
        "nome": "Corte premium",
        "ativo": True,
        "preco": 50.0,
        "duracao_em_minutos": 50,
        "pontos_gerados": 6,
    }
    historicos_encerrados = []
    historicos_criados = []

    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: current,
    )

    def fake_atualizar(received_conn, servico_id, data):
        assert received_conn is conn
        assert servico_id == 1
        assert data == {"nome": "Corte premium"}
        return {"id_servico": 1, "nome": "Corte premium", "ativo": True}

    monkeypatch.setattr(servico_service.servico_repository, "atualizar", fake_atualizar)
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "buscar_vigente",
        lambda _conn, _id: {"preco": 40.0, "duracao_em_minutos": 45, "pontos_gerados": 4},
    )
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "encerrar_vigente",
        lambda received_conn, servico_id: historicos_encerrados.append(
            (received_conn, servico_id)
        ),
    )
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        lambda _conn, **kwargs: historicos_criados.append(kwargs),
    )
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _conn, _id: updated)

    result = servico_service.atualizar_servico(
        conn,
        1,
        ServicoUpdate(nome="Corte premium", preco=50, duracao_em_minutos=50, pontos_gerados=6),
    )

    assert result == updated
    assert historicos_encerrados == [(conn, 1)]
    assert historicos_criados == [
        {
            "servico_id": 1,
            "preco": 50,
            "duracao_em_minutos": 50,
            "pontos_gerados": 6,
            "ativo": True,
        }
    ]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_servico_apenas_dados_principais_nao_cria_historico(monkeypatch):
    conn = FakeConn()
    historicos = []

    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1, "nome": "Corte premium", "ativo": True},
    )
    monkeypatch.setattr(servico_service.servico_repository, "atualizar", lambda _c, _id, _d: None)
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        lambda _conn, **kwargs: historicos.append(kwargs),
    )

    result = servico_service.atualizar_servico(conn, 1, ServicoUpdate(nome="Corte premium"))

    assert result["nome"] == "Corte premium"
    assert historicos == []
    assert conn.committed is True


def test_atualizar_servico_apenas_historico_preserva_dados_vigentes(monkeypatch):
    conn = FakeConn()
    created = []
    updated = {"id_servico": 1, "preco": 55, "duracao_em_minutos": 45, "pontos_gerados": 4}

    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _c, _id: updated)
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "buscar_vigente",
        lambda _c, _id: {"preco": 40, "duracao_em_minutos": 45, "pontos_gerados": 4},
    )
    monkeypatch.setattr(servico_service.historico_servico_repository, "encerrar_vigente", lambda *_: None)
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        lambda _conn, **kwargs: created.append(kwargs),
    )

    result = servico_service.atualizar_servico(conn, 1, ServicoUpdate(preco=55))

    assert result == updated
    assert created == [
        {
            "servico_id": 1,
            "preco": 55,
            "duracao_em_minutos": 45,
            "pontos_gerados": 4,
            "ativo": True,
        }
    ]
    assert conn.committed is True


def test_atualizar_servico_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        servico_service.atualizar_servico(
            conn,
            999,
            ServicoUpdate(nome="Corte premium"),
        )

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_atualizar_servico_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1},
    )

    def fake_atualizar(_conn, _servico_id, _data):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(servico_service.servico_repository, "atualizar", fake_atualizar)

    with pytest.raises(RuntimeError):
        servico_service.atualizar_servico(
            conn,
            1,
            ServicoUpdate(nome="Corte premium"),
        )

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_listar_historico_servico_existente_retorna_historico(monkeypatch):
    conn = FakeConn()
    rows = [{"id_historico": 1, "SERVICO_id_servico": 1}]
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1},
    )
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "listar_por_servico",
        lambda _conn, _id: rows,
    )

    result = servico_service.listar_historico_servico(conn, 1)

    assert result == rows
    assert conn.started is False


def test_listar_historico_servico_inexistente_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        servico_service.listar_historico_servico(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is False


def test_deletar_servico_existente_sem_vinculo_controla_transacao(monkeypatch):
    conn = FakeConn()
    deleted_ids = []
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1},
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "existe_atendimento_vinculado",
        lambda _conn, _id: False,
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "deletar",
        lambda _conn, servico_id: deleted_ids.append(servico_id),
    )

    result = servico_service.deletar_servico(conn, 1)

    assert result is None
    assert deleted_ids == [1]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_deletar_servico_inexistente_faz_rollback_e_retorna_404(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(servico_service.servico_repository, "buscar_por_id", lambda _conn, _id: None)

    with pytest.raises(HTTPException) as exc:
        servico_service.deletar_servico(conn, 404)

    assert exc.value.status_code == 404
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_servico_com_atendimento_vinculado_faz_rollback_e_retorna_409(monkeypatch):
    conn = FakeConn()
    deleted = False

    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1},
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "existe_atendimento_vinculado",
        lambda _conn, _id: True,
    )

    def fake_deletar(_conn, _id):
        nonlocal deleted
        deleted = True

    monkeypatch.setattr(servico_service.servico_repository, "deletar", fake_deletar)

    with pytest.raises(HTTPException) as exc:
        servico_service.deletar_servico(conn, 1)

    assert exc.value.status_code == 409
    assert deleted is False
    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True


def test_deletar_servico_faz_rollback_quando_repository_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {"id_servico": 1},
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "existe_atendimento_vinculado",
        lambda _conn, _id: False,
    )

    def fake_deletar(_conn, _servico_id):
        raise RuntimeError("erro de banco")

    monkeypatch.setattr(servico_service.servico_repository, "deletar", fake_deletar)

    with pytest.raises(RuntimeError):
        servico_service.deletar_servico(conn, 1)

    assert conn.started is True
    assert conn.committed is False
    assert conn.rolled_back is True
