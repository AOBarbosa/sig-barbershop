from fastapi import HTTPException

from app.repositories import pessoa_repository
from app.schemas.pessoa_schema import PessoaCreate, PessoaUpdate


def listar_pessoas(conn):
    return pessoa_repository.listar(conn)


def buscar_pessoa(conn, pessoa_id: int):
    pessoa = pessoa_repository.buscar_por_id(conn, pessoa_id)
    if pessoa is None:
        raise HTTPException(status_code=404, detail="Pessoa nao encontrada")
    return pessoa


def criar_pessoa(conn, payload: PessoaCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_cpf(conn, payload.cpf) is not None:
            raise HTTPException(status_code=409, detail="CPF ja cadastrado")
        if payload.email and pessoa_repository.buscar_por_email(conn, payload.email) is not None:
            raise HTTPException(status_code=409, detail="Email ja cadastrado")

        pessoa = pessoa_repository.criar(conn, payload.model_dump())
        conn.commit()
        return pessoa
    except Exception:
        conn.rollback()
        raise


def atualizar_pessoa(conn, pessoa_id: int, payload: PessoaUpdate):
    conn.start_transaction()
    try:
        pessoa_atual = pessoa_repository.buscar_por_id(conn, pessoa_id)
        if pessoa_atual is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        data = payload.model_dump(exclude_unset=True)

        if "cpf" in data and data["cpf"] != pessoa_atual["cpf"]:
            existente = pessoa_repository.buscar_por_cpf(conn, data["cpf"])
            if existente is not None and existente["id_pessoa"] != pessoa_id:
                raise HTTPException(status_code=409, detail="CPF ja cadastrado")

        if "email" in data and data["email"] and data["email"] != pessoa_atual["email"]:
            existente = pessoa_repository.buscar_por_email(conn, data["email"])
            if existente is not None and existente["id_pessoa"] != pessoa_id:
                raise HTTPException(status_code=409, detail="Email ja cadastrado")

        pessoa = pessoa_repository.atualizar(conn, pessoa_id, data)
        conn.commit()
        return pessoa
    except Exception:
        conn.rollback()
        raise


def deletar_pessoa(conn, pessoa_id: int):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, pessoa_id) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        if pessoa_repository.existe_vinculo(conn, pessoa_id):
            raise HTTPException(
                status_code=409,
                detail="Pessoa possui vinculos (cliente, barbeiro ou caixa)",
            )

        pessoa_repository.deletar(conn, pessoa_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
