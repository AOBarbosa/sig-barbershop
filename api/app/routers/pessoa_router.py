from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.pessoa_schema import PessoaCreate, PessoaResponse, PessoaUpdate
from app.schemas.telefone_schema import TelefoneResponse
from app.services import pessoa_service, telefone_service

router = APIRouter(prefix="/pessoas", tags=["pessoas"])


@router.get("", response_model=list[PessoaResponse])
def listar_pessoas(conn=Depends(get_db)):
    return pessoa_service.listar_pessoas(conn)


@router.get("/{pessoa_id}", response_model=PessoaResponse)
def buscar_pessoa(pessoa_id: int, conn=Depends(get_db)):
    return pessoa_service.buscar_pessoa(conn, pessoa_id)


@router.get("/{pessoa_id}/telefones", response_model=list[TelefoneResponse])
def listar_telefones_da_pessoa(pessoa_id: int, conn=Depends(get_db)):
    return telefone_service.listar_por_pessoa(conn, pessoa_id)


@router.post("", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
def criar_pessoa(payload: PessoaCreate, conn=Depends(get_db)):
    return pessoa_service.criar_pessoa(conn, payload)


@router.put("/{pessoa_id}", response_model=PessoaResponse)
def atualizar_pessoa(pessoa_id: int, payload: PessoaUpdate, conn=Depends(get_db)):
    return pessoa_service.atualizar_pessoa(conn, pessoa_id, payload)


@router.delete("/{pessoa_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pessoa(pessoa_id: int, conn=Depends(get_db)):
    pessoa_service.deletar_pessoa(conn, pessoa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
