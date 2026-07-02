from fastapi import HTTPException

from app.repositories import historico_servico_repository, servico_repository
from app.schemas.servico_schema import ServicoCreate, ServicoUpdate


def listar_servicos(conn):
    return servico_repository.listar(conn)


def buscar_servico(conn, servico_id: int):
    servico = servico_repository.buscar_por_id(conn, servico_id)
    if servico is None:
        raise HTTPException(status_code=404, detail="Servico nao encontrado")
    return servico


def listar_historico_servico(conn, servico_id: int):
    if servico_repository.buscar_por_id(conn, servico_id) is None:
        raise HTTPException(status_code=404, detail="Servico nao encontrado")
    return historico_servico_repository.listar_por_servico(conn, servico_id)


def criar_servico(conn, payload: ServicoCreate):
    conn.start_transaction()
    try:
        servico = servico_repository.criar(conn, payload.model_dump())
        conn.commit()
        return servico
    except Exception:
        conn.rollback()
        raise


def atualizar_servico(conn, servico_id: int, payload: ServicoUpdate):
    conn.start_transaction()
    try:
        servico_atual = servico_repository.buscar_por_id(conn, servico_id)
        if servico_atual is None:
            raise HTTPException(status_code=404, detail="Servico nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        servico = servico_repository.atualizar(conn, servico_id, data)
        historico_servico_repository.criar(
            conn,
            servico_id=servico_id,
            preco_anterior=servico_atual["preco"],
            preco_novo=servico["preco"],
            ativo=bool(servico["ativo"]),
        )
        conn.commit()
        return servico
    except Exception:
        conn.rollback()
        raise


def deletar_servico(conn, servico_id: int):
    conn.start_transaction()
    try:
        if servico_repository.buscar_por_id(conn, servico_id) is None:
            raise HTTPException(status_code=404, detail="Servico nao encontrado")

        if servico_repository.existe_atendimento_vinculado(conn, servico_id):
            raise HTTPException(
                status_code=409,
                detail="Servico possui atendimentos vinculados",
            )

        servico_repository.deletar(conn, servico_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
