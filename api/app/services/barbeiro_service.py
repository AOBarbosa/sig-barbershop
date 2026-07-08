from fastapi import HTTPException

from app.repositories import barbeiro_repository, pessoa_repository
from app.schemas.barbeiro_schema import (
    BarbeiroCompletoCreate,
    BarbeiroCompletoUpdate,
    BarbeiroCreate,
    BarbeiroUpdate,
)


def listar_barbeiros(conn):
    return barbeiro_repository.listar(conn)


def buscar_barbeiro(conn, barbeiro_id: int):
    barbeiro = barbeiro_repository.buscar_por_id(conn, barbeiro_id)
    if barbeiro is None:
        raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")
    return barbeiro


def criar_barbeiro(conn, payload: BarbeiroCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_id(conn, payload.PESSOA_id_pessoa) is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        if barbeiro_repository.buscar_por_pessoa(conn, payload.PESSOA_id_pessoa) is not None:
            raise HTTPException(status_code=409, detail="Pessoa ja esta cadastrada como barbeiro")

        barbeiro = barbeiro_repository.criar(conn, payload.model_dump())
        conn.commit()
        return barbeiro
    except Exception:
        conn.rollback()
        raise


def _barbeiro_completo_pessoa_data(payload: BarbeiroCompletoCreate):
    return {
        "nome": payload.nome,
        "cpf": payload.cpf,
        "email": payload.email,
        "data_nascimento": payload.data_nascimento,
        "admin": payload.admin,
    }


def _barbeiro_completo_data(payload: BarbeiroCompletoCreate, pessoa_id: int):
    return {
        "PESSOA_id_pessoa": pessoa_id,
        "apelido": payload.apelido,
        "comissao_percentual": payload.comissao_percentual,
    }


def criar_barbeiro_completo(conn, payload: BarbeiroCompletoCreate):
    conn.start_transaction()
    try:
        if pessoa_repository.buscar_por_cpf(conn, payload.cpf) is not None:
            raise HTTPException(status_code=409, detail="CPF ja cadastrado")

        if payload.email and pessoa_repository.buscar_por_email(conn, payload.email) is not None:
            raise HTTPException(status_code=409, detail="Email ja cadastrado")

        pessoa = pessoa_repository.criar(conn, _barbeiro_completo_pessoa_data(payload))
        barbeiro = barbeiro_repository.criar(
            conn,
            _barbeiro_completo_data(payload, pessoa["id_pessoa"]),
        )
        conn.commit()
        return {"barbeiro": barbeiro, "pessoa": pessoa}
    except Exception:
        conn.rollback()
        raise


def _validar_cpf_unico(conn, cpf: str, pessoa_id: int):
    existente = pessoa_repository.buscar_por_cpf(conn, cpf)
    if existente is not None and existente["id_pessoa"] != pessoa_id:
        raise HTTPException(status_code=409, detail="CPF ja cadastrado")


def _validar_email_unico(conn, email: str | None, pessoa_id: int):
    if not email:
        return

    existente = pessoa_repository.buscar_por_email(conn, email)
    if existente is not None and existente["id_pessoa"] != pessoa_id:
        raise HTTPException(status_code=409, detail="Email ja cadastrado")


def _separar_barbeiro_completo_update(data):
    pessoa_campos = {"nome", "cpf", "email", "data_nascimento", "admin"}
    pessoa_data = {campo: valor for campo, valor in data.items() if campo in pessoa_campos}
    barbeiro_data = {
        campo: valor
        for campo, valor in data.items()
        if campo in {"apelido", "comissao_percentual"}
    }
    return pessoa_data, barbeiro_data


def _validar_pessoa_update_unica(conn, pessoa_id: int, pessoa_atual, pessoa_data):
    if "cpf" in pessoa_data and pessoa_data["cpf"] != pessoa_atual["cpf"]:
        _validar_cpf_unico(conn, pessoa_data["cpf"], pessoa_id)
    if "email" in pessoa_data and pessoa_data["email"] != pessoa_atual["email"]:
        _validar_email_unico(conn, pessoa_data["email"], pessoa_id)


def atualizar_barbeiro_completo(conn, barbeiro_id: int, payload: BarbeiroCompletoUpdate):
    conn.start_transaction()
    try:
        atual = barbeiro_repository.buscar_por_id(conn, barbeiro_id)
        if atual is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        pessoa_id = atual["PESSOA_id_pessoa"]
        pessoa_atual = pessoa_repository.buscar_por_id(conn, pessoa_id)
        if pessoa_atual is None:
            raise HTTPException(status_code=404, detail="Pessoa nao encontrada")

        data = payload.model_dump(exclude_unset=True)
        pessoa_data, barbeiro_data = _separar_barbeiro_completo_update(data)
        _validar_pessoa_update_unica(conn, pessoa_id, pessoa_atual, pessoa_data)

        pessoa = pessoa_repository.atualizar(conn, pessoa_id, pessoa_data)
        barbeiro = barbeiro_repository.atualizar(conn, barbeiro_id, barbeiro_data)
        conn.commit()
        return {"barbeiro": barbeiro, "pessoa": pessoa}
    except Exception:
        conn.rollback()
        raise


def atualizar_barbeiro(conn, barbeiro_id: int, payload: BarbeiroUpdate):
    conn.start_transaction()
    try:
        if barbeiro_repository.buscar_por_id(conn, barbeiro_id) is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        data = payload.model_dump(exclude_unset=True)
        barbeiro = barbeiro_repository.atualizar(conn, barbeiro_id, data)
        conn.commit()
        return barbeiro
    except Exception:
        conn.rollback()
        raise


def deletar_barbeiro(conn, barbeiro_id: int):
    conn.start_transaction()
    try:
        if barbeiro_repository.buscar_por_id(conn, barbeiro_id) is None:
            raise HTTPException(status_code=404, detail="Barbeiro nao encontrado")

        if barbeiro_repository.existe_atendimento_vinculado(conn, barbeiro_id):
            raise HTTPException(
                status_code=409,
                detail="Barbeiro possui atendimentos vinculados",
            )

        barbeiro_repository.deletar(conn, barbeiro_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
