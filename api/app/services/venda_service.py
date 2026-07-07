from decimal import Decimal

from fastapi import HTTPException

from app.repositories import produto_repository, venda_produto_repository, venda_repository
from app.schemas.venda_schema import VendaCreate, VendaProdutoCreate, VendaStatusUpdate
from app.services import historico_pontos_service


def listar_vendas(conn):
    return venda_repository.listar(conn)


def buscar_venda(conn, venda_id: int):
    venda = venda_repository.buscar_por_id(conn, venda_id)
    if venda is None:
        raise HTTPException(status_code=404, detail="Venda nao encontrada")
    return venda


def _validar_cliente(conn, cliente_id: int):
    if not venda_repository.cliente_existe(conn, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")


def _validar_caixa(conn, caixa_id: int):
    if not venda_repository.caixa_existe(conn, caixa_id):
        raise HTTPException(status_code=404, detail="Caixa nao encontrado")


def _recalcular_valor_total(conn, venda_id: int):
    valor_total = venda_repository.calcular_valor_total(conn, venda_id)
    return venda_repository.atualizar_valor_total(conn, venda_id, valor_total)


def criar_venda(conn, payload: VendaCreate):
    conn.start_transaction()
    try:
        _validar_cliente(conn, payload.CLIENTE_id_cliente)
        _validar_caixa(conn, payload.CAIXA_id_caixa)

        data = payload.model_dump()
        data["valor_total"] = Decimal("0.00")
        data["status"] = "pendente"
        venda = venda_repository.criar(conn, data)
        venda = _recalcular_valor_total(conn, venda["id_venda"])
        conn.commit()
        return venda
    except Exception:
        conn.rollback()
        raise


def atualizar_status_venda(conn, venda_id: int, payload: VendaStatusUpdate):
    conn.start_transaction()
    try:
        venda_atual = venda_repository.buscar_por_id(conn, venda_id)
        if venda_atual is None:
            raise HTTPException(status_code=404, detail="Venda nao encontrada")

        venda = venda_repository.atualizar_status(conn, venda_id, payload.status)

        if payload.status == "concluida" and venda_atual["status"] != "concluida":
            historico_pontos_service.acumular_pontos_venda(
                conn,
                venda_id,
                venda_atual["CLIENTE_id_cliente"],
            )

        conn.commit()
        return venda
    except Exception:
        conn.rollback()
        raise


def deletar_venda(conn, venda_id: int):
    conn.start_transaction()
    try:
        if venda_repository.buscar_por_id(conn, venda_id) is None:
            raise HTTPException(status_code=404, detail="Venda nao encontrada")

        venda_repository.deletar(conn, venda_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def _validar_venda_existe(conn, venda_id: int):
    if venda_repository.buscar_por_id(conn, venda_id) is None:
        raise HTTPException(status_code=404, detail="Venda nao encontrada")


def _buscar_produto(conn, produto_id: int):
    produto = produto_repository.buscar_por_id(conn, produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return produto


def _buscar_vinculo_venda_produto(conn, venda_id: int, produto_id: int):
    vinculo = venda_produto_repository.buscar_por_ids(conn, venda_id, produto_id)
    if vinculo is None:
        raise HTTPException(status_code=404, detail="Produto nao vinculado a venda")
    return vinculo


def _validar_produto_disponivel_para_venda(conn, venda_id: int, produto_id: int):
    vinculo = venda_produto_repository.buscar_por_ids(conn, venda_id, produto_id)
    if vinculo is not None:
        raise HTTPException(status_code=409, detail="Produto ja vinculado a venda")


def listar_produtos_venda(conn, venda_id: int):
    _validar_venda_existe(conn, venda_id)
    return venda_produto_repository.listar_por_venda(conn, venda_id)


def adicionar_produto_venda(conn, venda_id: int, payload: VendaProdutoCreate):
    conn.start_transaction()
    try:
        _validar_venda_existe(conn, venda_id)
        produto = _buscar_produto(conn, payload.PRODUTO_id_produto)
        _validar_produto_disponivel_para_venda(conn, venda_id, payload.PRODUTO_id_produto)

        if produto["estoque"] < payload.quantidade:
            raise HTTPException(status_code=422, detail="Estoque insuficiente")

        produto_repository.atualizar(
            conn,
            payload.PRODUTO_id_produto,
            {"estoque": produto["estoque"] - payload.quantidade},
        )
        vinculo = venda_produto_repository.criar(
            conn,
            venda_id=venda_id,
            produto_id=payload.PRODUTO_id_produto,
            quantidade=payload.quantidade,
            preco_unitario=produto["preco"],
        )
        _recalcular_valor_total(conn, venda_id)
        conn.commit()
        return vinculo
    except Exception:
        conn.rollback()
        raise


def remover_produto_venda(conn, venda_id: int, produto_id: int):
    conn.start_transaction()
    try:
        _validar_venda_existe(conn, venda_id)
        vinculo = _buscar_vinculo_venda_produto(conn, venda_id, produto_id)
        produto = _buscar_produto(conn, produto_id)

        produto_repository.atualizar(
            conn,
            produto_id,
            {"estoque": produto["estoque"] + vinculo["quantidade"]},
        )
        venda_produto_repository.deletar_por_ids(conn, venda_id, produto_id)
        _recalcular_valor_total(conn, venda_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
