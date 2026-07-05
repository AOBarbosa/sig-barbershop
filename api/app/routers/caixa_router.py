from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.caixa_schema import CaixaCreate, CaixaResponse
from app.services import caixa_service

router = APIRouter(prefix="/caixas", tags=["caixas"])


@router.get("", response_model=list[CaixaResponse])
def listar_caixas(conn=Depends(get_db)):
    return caixa_service.listar_caixas(conn)


@router.get("/{caixa_id}", response_model=CaixaResponse)
def buscar_caixa(caixa_id: int, conn=Depends(get_db)):
    return caixa_service.buscar_caixa(conn, caixa_id)


@router.post("", response_model=CaixaResponse, status_code=status.HTTP_201_CREATED)
def criar_caixa(payload: CaixaCreate, conn=Depends(get_db)):
    return caixa_service.criar_caixa(conn, payload)


@router.delete("/{caixa_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_caixa(caixa_id: int, conn=Depends(get_db)):
    caixa_service.deletar_caixa(conn, caixa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
