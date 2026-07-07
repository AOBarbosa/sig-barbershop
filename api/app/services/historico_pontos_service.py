from fastapi import HTTPException

from app.repositories import (
    atendimento_servico_repository,
    cliente_repository,
    fidelidade_repository,
    historico_pontos_repository,
    venda_produto_repository,
)


def _validar_cliente_existe(conn, cliente_id: int):
    if cliente_repository.buscar_por_id(conn, cliente_id) is None:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")


def buscar_saldo_pontos(conn, cliente_id: int):
    _validar_cliente_existe(conn, cliente_id)
    saldo = historico_pontos_repository.calcular_saldo(conn, cliente_id)
    return {"CLIENTE_id_cliente": cliente_id, "saldo": saldo}


def listar_historico_pontos(conn, cliente_id: int):
    _validar_cliente_existe(conn, cliente_id)
    return historico_pontos_repository.listar_por_cliente(conn, cliente_id)


def acumular_pontos_atendimento(conn, atendimento_id: int, cliente_id: int):
    servicos = atendimento_servico_repository.listar_por_atendimento(conn, atendimento_id)

    total_pontos = 0
    for vinculo in servicos:
        regra = fidelidade_repository.buscar_por_servico(conn, vinculo["SERVICO_id_servico"])
        if regra is not None:
            total_pontos += regra["pontos"]

    if total_pontos > 0:
        historico_pontos_repository.criar(
            conn,
            cliente_id,
            total_pontos,
            "acumulo",
            f"Atendimento #{atendimento_id} concluido",
        )

    return total_pontos


def acumular_pontos_venda(conn, venda_id: int, cliente_id: int):
    produtos = venda_produto_repository.listar_por_venda(conn, venda_id)

    total_pontos = 0
    for vinculo in produtos:
        regra = fidelidade_repository.buscar_por_produto(conn, vinculo["PRODUTO_id_produto"])
        if regra is not None:
            total_pontos += regra["pontos"] * vinculo["quantidade"]

    if total_pontos > 0:
        historico_pontos_repository.criar(
            conn,
            cliente_id,
            total_pontos,
            "acumulo",
            f"Venda #{venda_id} concluida",
        )

    return total_pontos
