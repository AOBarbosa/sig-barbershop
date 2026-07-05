from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.cliente_schema import ClienteCreate, ClienteResponse
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
def listar_clientes(conn=Depends(get_db)):
    return cliente_service.listar_clientes(conn)


@router.get("/{cliente_id}", response_model=ClienteResponse)
def buscar_cliente(cliente_id: int, conn=Depends(get_db)):
    return cliente_service.buscar_cliente(conn, cliente_id)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(payload: ClienteCreate, conn=Depends(get_db)):
    return cliente_service.criar_cliente(conn, payload)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, conn=Depends(get_db)):
    cliente_service.deletar_cliente(conn, cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
