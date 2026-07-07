from fastapi import HTTPException

from app.repositories import cliente_repository, pessoa_repository
from app.schemas.cliente_schema import ClienteCompletoCreate, ClienteCreate


def listar_clientes(conn):
    return cliente_repository.listar(conn)


def buscar_cliente(conn, cliente_id: int):
    cliente = cliente_repository.buscar_por_id(conn, cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return cliente


def criar_cliente(conn, payload: ClienteCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, payload.PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        if cliente_repository.buscar_por_pessoa(conn, payload.PESSOA_id_pessoa) is not None:
            raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como cliente")

        cliente = cliente_repository.criar(conn, payload.model_dump())
        conn.commit()
        return cliente
    except Exception:
        conn.rollback()
        raise


def criar_cliente_completo(conn, payload: ClienteCompletoCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_cpf(conn, payload.cpf) is not None:
            raise HTTPException(status_code=409, detail="CPF ja cadastrado")

        if payload.email and pessoa_repository.buscar_por_email(conn, payload.email) is not None:
            raise HTTPException(status_code=409, detail="Email ja cadastrado")

        pessoa = pessoa_repository.criar(conn, payload.model_dump())
        cliente = cliente_repository.criar(
            conn, {"PESSOA_id_pessoa": pessoa["id_pessoa"]}
        )
        conn.commit()
        return {"cliente": cliente, "pessoa": pessoa}
    except Exception:
        conn.rollback()
        raise


def deletar_cliente(conn, cliente_id: int):
    conn.start_transaction()
    try:
        if cliente_repository.buscar_por_id(conn, cliente_id) is None:
            raise HTTPException(status_code=404, detail="Cliente nao encontrado")

        if cliente_repository.existe_vinculo(conn, cliente_id):
            raise HTTPException(
                status_code=409,
                detail="Cliente possui atendimentos, vendas ou historico de pontos",
            )

        cliente_repository.deletar(conn, cliente_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
