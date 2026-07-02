from decimal import Decimal

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
        "descricao": "Corte masculino",
        "preco": Decimal("35.00"),
        "duracao_minutos": 30,
        "ativo": True,
    }

    def fake_criar(received_conn, data):
        assert received_conn is conn
        assert data["nome"] == "Corte"
        return created

    monkeypatch.setattr(servico_service.servico_repository, "criar", fake_criar)

    result = servico_service.criar_servico(
        conn,
        ServicoCreate(
            nome="Corte",
            descricao="Corte masculino",
            preco=Decimal("35.00"),
            duracao_minutos=30,
            ativo=True,
        ),
    )

    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False
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
                descricao=None,
                preco=Decimal("35.00"),
                duracao_minutos=30,
                ativo=True,
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
        "preco": Decimal("35.00"),
        "ativo": True,
    }
    updated = {
        "id_servico": 1,
        "nome": "Corte premium",
        "preco": Decimal("35.00"),
        "ativo": True,
    }
    historicos = []

    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: current,
    )

    def fake_atualizar(received_conn, servico_id, data):
        assert received_conn is conn
        assert servico_id == 1
        assert data == {"nome": "Corte premium"}
        return updated

    monkeypatch.setattr(servico_service.servico_repository, "atualizar", fake_atualizar)
    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        lambda *args, **kwargs: historicos.append((args, kwargs)),
    )

    result = servico_service.atualizar_servico(
        conn,
        1,
        ServicoUpdate(nome="Corte premium"),
    )

    assert result == updated
    assert historicos == [
        (
            (conn,),
            {
                "servico_id": 1,
                "preco_anterior": Decimal("35.00"),
                "preco_novo": Decimal("35.00"),
                "ativo": True,
            },
        )
    ]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


def test_atualizar_servico_grava_historico_com_preco_anterior_preco_novo_e_ativo(monkeypatch):
    conn = FakeConn()
    current = {
        "id_servico": 1,
        "nome": "Corte",
        "preco": Decimal("35.00"),
        "ativo": True,
    }
    updated = {
        "id_servico": 1,
        "nome": "Corte",
        "preco": Decimal("45.00"),
        "ativo": False,
    }
    historicos = []

    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: current,
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "atualizar",
        lambda _conn, _id, _data: updated,
    )

    def fake_criar_historico(received_conn, **data):
        assert received_conn is conn
        historicos.append(data)

    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        fake_criar_historico,
    )

    result = servico_service.atualizar_servico(
        conn,
        1,
        ServicoUpdate(preco=Decimal("45.00"), ativo=False),
    )

    assert result == updated
    assert historicos == [
        {
            "servico_id": 1,
            "preco_anterior": Decimal("35.00"),
            "preco_novo": Decimal("45.00"),
            "ativo": False,
        }
    ]
    assert conn.started is True
    assert conn.committed is True
    assert conn.rolled_back is False


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


def test_atualizar_servico_faz_rollback_quando_historico_falha(monkeypatch):
    conn = FakeConn()
    monkeypatch.setattr(
        servico_service.servico_repository,
        "buscar_por_id",
        lambda _conn, _id: {
            "id_servico": 1,
            "preco": Decimal("35.00"),
            "ativo": True,
        },
    )
    monkeypatch.setattr(
        servico_service.servico_repository,
        "atualizar",
        lambda _conn, _id, _data: {
            "id_servico": 1,
            "preco": Decimal("45.00"),
            "ativo": True,
        },
    )

    def fake_criar_historico(_conn, **_data):
        raise RuntimeError("erro no historico")

    monkeypatch.setattr(
        servico_service.historico_servico_repository,
        "criar",
        fake_criar_historico,
    )

    with pytest.raises(RuntimeError):
        servico_service.atualizar_servico(
            conn,
            1,
            ServicoUpdate(preco=Decimal("45.00")),
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
