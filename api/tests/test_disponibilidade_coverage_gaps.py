from datetime import time

from app.schemas.disponibilidade_schema import DiaSemana, DisponibilidadeUpdate
from app.services import disponibilidade_service


class FakeConn:
    def __init__(self):
        self.committed = False

    def start_transaction(self):
        pass

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def disponibilidade_row(dia="segunda"):
    return {
        "id_disponibilidade": 1,
        "BARBEIRO_id_barbeiro": 1,
        "dia_semana": dia,
        "hora_inicio": time(9, 0),
        "hora_fim": time(18, 0),
    }


def test_atualizar_disponibilidade_mantem_mesmo_dia_sem_buscar_conflito(monkeypatch):
    conn = FakeConn()
    atual = disponibilidade_row(dia="segunda")
    chamadas_conflito = []

    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_id",
        lambda _c, _i: atual,
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "buscar_por_barbeiro_e_dia",
        lambda *_args: chamadas_conflito.append(_args),
    )
    monkeypatch.setattr(
        disponibilidade_service.disponibilidade_repository,
        "atualizar",
        lambda _c, _i, _d: atual,
    )

    result = disponibilidade_service.atualizar_disponibilidade(
        conn, 1, DisponibilidadeUpdate(dia_semana=DiaSemana.segunda)
    )

    assert result == atual
    assert chamadas_conflito == []
    assert conn.committed is True
