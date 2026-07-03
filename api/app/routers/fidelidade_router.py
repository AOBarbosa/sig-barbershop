from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.fidelidade_schema import (
    FidelidadeCreate,
    FidelidadeResponse,
    FidelidadeUpdate,
)
from app.services import fidelidade_service

router = APIRouter(prefix="/fidelidades", tags=["fidelidades"])


@router.get("", response_model=list[FidelidadeResponse])
def listar_fidelidades(conn=Depends(get_db)):
    return fidelidade_service.listar_fidelidades(conn)


@router.get("/{fidelidade_id}", response_model=FidelidadeResponse)
def buscar_fidelidade(fidelidade_id: int, conn=Depends(get_db)):
    return fidelidade_service.buscar_fidelidade(conn, fidelidade_id)


@router.post("", response_model=FidelidadeResponse, status_code=status.HTTP_201_CREATED)
def criar_fidelidade(payload: FidelidadeCreate, conn=Depends(get_db)):
    return fidelidade_service.criar_fidelidade(conn, payload)


@router.put("/{fidelidade_id}", response_model=FidelidadeResponse)
def atualizar_fidelidade(fidelidade_id: int, payload: FidelidadeUpdate, conn=Depends(get_db)):
    return fidelidade_service.atualizar_fidelidade(conn, fidelidade_id, payload)


@router.delete("/{fidelidade_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_fidelidade(fidelidade_id: int, conn=Depends(get_db)):
    fidelidade_service.deletar_fidelidade(conn, fidelidade_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
