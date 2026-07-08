from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException

from app.repositories import (
    atendimento_repository,
    atendimento_servico_repository,
    cliente_repository,
    fidelidade_repository,
    historico_pontos_repository,
    venda_produto_repository,
    venda_repository,
)


def _validar_cliente_existe(conn, cliente_id: int):
    if cliente_repository.buscar_por_id(conn, cliente_id) is None:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")


def buscar_saldo_pontos(conn, cliente_id: int):
    _validar_cliente_existe(conn, cliente_id)
    saldo = historico_pontos_repository.calcular_saldo(conn, cliente_id)
    return {"CLIENTE_PESSOA_id_pessoa": cliente_id, "saldo": saldo}


def listar_historico_pontos(conn, cliente_id: int):
    _validar_cliente_existe(conn, cliente_id)
    return historico_pontos_repository.listar_por_cliente(conn, cliente_id)


def _pontos_acumulados(regra: dict) -> int:
    return regra.get("pontos_acumulados", regra.get("pontos", 0))


def _buscar_caixa_padrao(conn) -> int:
    caixa = venda_repository.buscar_primeiro_caixa(conn)
    if caixa is None:
        raise HTTPException(status_code=422, detail="Nenhum caixa cadastrado para registrar pontos")
    return caixa["PESSOA_id_pessoa"]


def _criar_venda_do_atendimento(conn, atendimento_id: int, cliente_id: int) -> int:
    atendimento = atendimento_repository.buscar_por_id(conn, atendimento_id)
    valor_total = atendimento["valor_total"] if atendimento else Decimal("0.00")
    venda = venda_repository.criar(
        conn,
        {
            "CLIENTE_PESSOA_id_pessoa": cliente_id,
            "CAIXA_PESSOA_id_pessoa": _buscar_caixa_padrao(conn),
            "data_hora": datetime.now(),
            "valor_total": valor_total,
            "status": "PAGA",
            "forma_pagamento": "OUTRO",
            "desconto": Decimal("0.00"),
        },
    )
    return venda["id_venda"]


def acumular_pontos_atendimento(conn, atendimento_id: int, cliente_id: int):
    servicos = atendimento_servico_repository.listar_por_atendimento(conn, atendimento_id)

    movimentos = []
    total_pontos = 0
    for vinculo in servicos:
        regra = fidelidade_repository.buscar_por_servico(conn, vinculo["SERVICO_id_servico"])
        if regra is not None:
            pontos = _pontos_acumulados(regra)
            if pontos > 0:
                movimentos.append((regra["id_fidelidade"], pontos))
                total_pontos += pontos

    if movimentos:
        venda_id = _criar_venda_do_atendimento(conn, atendimento_id, cliente_id)
        for fidelidade_id, pontos in movimentos:
            historico_pontos_repository.criar(
                conn,
                cliente_id,
                venda_id,
                fidelidade_id,
                pontos,
                "ACUMULA",
            )

    return total_pontos


def acumular_pontos_venda(conn, venda_id: int, cliente_id: int):
    produtos = venda_produto_repository.listar_por_venda(conn, venda_id)

    total_pontos = 0
    for vinculo in produtos:
        regra = fidelidade_repository.buscar_por_produto(conn, vinculo["PRODUTO_id_produto"])
        if regra is not None:
            pontos = _pontos_acumulados(regra) * vinculo["quantidade"]
            if pontos <= 0:
                continue
            total_pontos += pontos
            historico_pontos_repository.criar(
                conn,
                cliente_id,
                venda_id,
                regra["id_fidelidade"],
                pontos,
                "ACUMULA",
            )

    return total_pontos
