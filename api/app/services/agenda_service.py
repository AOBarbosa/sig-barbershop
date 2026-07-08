from app.repositories import agenda_repository


def listar_horarios_ocupados(conn, barbeiro_id: int, inicio, fim):
    return agenda_repository.listar_horarios_ocupados_barbeiro(
        conn,
        barbeiro_id,
        inicio,
        fim,
    )
