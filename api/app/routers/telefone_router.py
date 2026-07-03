from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.telefone_schema import TelefoneCreate, TelefoneResponse, TelefoneUpdate
from app.services import telefone_service

router = APIRouter(prefix="/telefones", tags=["telefones"])


@router.get("/{telefone_id}", response_model=TelefoneResponse)
def buscar_telefone(telefone_id: int, conn=Depends(get_db)):
    return telefone_service.buscar_telefone(conn, telefone_id)


@router.post("", response_model=TelefoneResponse, status_code=status.HTTP_201_CREATED)
def criar_telefone(payload: TelefoneCreate, conn=Depends(get_db)):
    return telefone_service.criar_telefone(conn, payload)


@router.put("/{telefone_id}", response_model=TelefoneResponse)
def atualizar_telefone(telefone_id: int, payload: TelefoneUpdate, conn=Depends(get_db)):
    return telefone_service.atualizar_telefone(conn, telefone_id, payload)


@router.delete("/{telefone_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_telefone(telefone_id: int, conn=Depends(get_db)):
    telefone_service.deletar_telefone(conn, telefone_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
