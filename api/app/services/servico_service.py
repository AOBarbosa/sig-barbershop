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
        data = payload.model_dump()
        servico_data = {
            "nome": data["nome"],
            "ativo": data["ativo"],
        }
        servico = servico_repository.criar(conn, servico_data)
        historico_servico_repository.criar(
            conn,
            servico_id=servico["id_servico"],
            preco=data["preco"],
            duracao_em_minutos=data["duracao_em_minutos"],
            pontos_gerados=data["pontos_gerados"],
            ativo=True,
        )
        servico = servico_repository.buscar_por_id(conn, servico["id_servico"])
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
        servico_data = {
            key: data[key]
            for key in ("nome", "ativo")
            if key in data
        }
        historico_data = {
            key: data[key]
            for key in ("preco", "duracao_em_minutos", "pontos_gerados")
            if key in data
        }

        if servico_data:
            servico_repository.atualizar(conn, servico_id, servico_data)
        if historico_data:
            vigente = historico_servico_repository.buscar_vigente(conn, servico_id) or {}
            novo_historico = {
                "preco": historico_data.get("preco", vigente.get("preco")),
                "duracao_em_minutos": historico_data.get(
                    "duracao_em_minutos",
                    vigente.get("duracao_em_minutos"),
                ),
                "pontos_gerados": historico_data.get(
                    "pontos_gerados",
                    vigente.get("pontos_gerados", 0),
                ),
            }
            historico_servico_repository.encerrar_vigente(conn, servico_id)
            historico_servico_repository.criar(
                conn,
                servico_id=servico_id,
                ativo=True,
                **novo_historico,
            )

        servico = servico_repository.buscar_por_id(conn, servico_id)
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
