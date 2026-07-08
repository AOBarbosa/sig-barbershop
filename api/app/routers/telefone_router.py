from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db, require_funcionario
from app.schemas.telefone_schema import TelefoneCreate, TelefoneResponse, TelefoneUpdate
from app.services import telefone_service

router = APIRouter(
    prefix="/telefones", tags=["telefones"], dependencies=[Depends(require_funcionario)]
)


@router.get("/{pessoa_id}/{telefone}", response_model=TelefoneResponse)
def buscar_telefone(pessoa_id: int, telefone: str, conn=Depends(get_db)):
    return telefone_service.buscar_telefone(conn, pessoa_id, telefone)


@router.post("", response_model=TelefoneResponse, status_code=status.HTTP_201_CREATED)
def criar_telefone(payload: TelefoneCreate, conn=Depends(get_db)):
    return telefone_service.criar_telefone(conn, payload)


@router.put("/{pessoa_id}/{telefone}", response_model=TelefoneResponse)
def atualizar_telefone(
    pessoa_id: int, telefone: str, payload: TelefoneUpdate, conn=Depends(get_db)
):
    return telefone_service.atualizar_telefone(conn, pessoa_id, telefone, payload)


@router.delete("/{pessoa_id}/{telefone}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_telefone(pessoa_id: int, telefone: str, conn=Depends(get_db)):
    telefone_service.deletar_telefone(conn, pessoa_id, telefone)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
