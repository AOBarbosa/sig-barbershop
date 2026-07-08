import inspect

from app.services import agenda_service


def test_listar_horarios_ocupados_delega_para_repository(monkeypatch):
    called = {}

    def fake(conn, barbeiro_id, inicio, fim):
        called["args"] = (conn, barbeiro_id, inicio, fim)
        return [{"data_hora_inicio": "2026-07-13T08:30:00"}]

    monkeypatch.setattr(
        agenda_service.agenda_repository,
        "listar_horarios_ocupados_barbeiro",
        fake,
    )

    conn = object()
    result = agenda_service.listar_horarios_ocupados(
        conn,
        2,
        "2026-07-13T00:00:00",
        "2026-07-27T23:59:59",
    )

    assert called["args"] == (
        conn,
        2,
        "2026-07-13T00:00:00",
        "2026-07-27T23:59:59",
    )
    assert result == [{"data_hora_inicio": "2026-07-13T08:30:00"}]


def test_service_nao_controla_transacao():
    source = inspect.getsource(agenda_service)
    assert "commit" not in source
    assert "rollback" not in source
