from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.venda_schema import VendaCreate, VendaResponse, VendaStatusUpdate
from app.services import venda_service

router = APIRouter(prefix="/vendas", tags=["vendas"])


@router.get("", response_model=list[VendaResponse])
def listar_vendas(conn=Depends(get_db)):
    return venda_service.listar_vendas(conn)


@router.get("/{venda_id}", response_model=VendaResponse)
def buscar_venda(venda_id: int, conn=Depends(get_db)):
    return venda_service.buscar_venda(conn, venda_id)


@router.post("", response_model=VendaResponse, status_code=status.HTTP_201_CREATED)
def criar_venda(payload: VendaCreate, conn=Depends(get_db)):
    return venda_service.criar_venda(conn, payload)


@router.patch("/{venda_id}/status", response_model=VendaResponse)
def atualizar_status_venda(venda_id: int, payload: VendaStatusUpdate, conn=Depends(get_db)):
    return venda_service.atualizar_status_venda(conn, venda_id, payload)


@router.delete("/{venda_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_venda(venda_id: int, conn=Depends(get_db)):
    venda_service.deletar_venda(conn, venda_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
