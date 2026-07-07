from decimal import Decimal

from fastapi import HTTPException

from app.repositories import venda_repository
from app.schemas.venda_schema import VendaCreate, VendaStatusUpdate


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
        if venda_repository.buscar_por_id(conn, venda_id) is None:
            raise HTTPException(status_code=404, detail="Venda nao encontrada")

        venda = venda_repository.atualizar_status(conn, venda_id, payload.status)
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
