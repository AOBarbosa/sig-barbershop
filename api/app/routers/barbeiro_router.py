from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.barbeiro_schema import BarbeiroCreate, BarbeiroResponse, BarbeiroUpdate
from app.schemas.disponibilidade_schema import DisponibilidadeResponse
from app.services import barbeiro_service, disponibilidade_service

router = APIRouter(prefix="/barbeiros", tags=["barbeiros"])


@router.get("", response_model=list[BarbeiroResponse])
def listar_barbeiros(conn=Depends(get_db)):
    return barbeiro_service.listar_barbeiros(conn)


@router.get("/{barbeiro_id}", response_model=BarbeiroResponse)
def buscar_barbeiro(barbeiro_id: int, conn=Depends(get_db)):
    return barbeiro_service.buscar_barbeiro(conn, barbeiro_id)


@router.get("/{barbeiro_id}/disponibilidades", response_model=list[DisponibilidadeResponse])
def listar_disponibilidades_do_barbeiro(barbeiro_id: int, conn=Depends(get_db)):
    return disponibilidade_service.listar_por_barbeiro(conn, barbeiro_id)


@router.post("", response_model=BarbeiroResponse, status_code=status.HTTP_201_CREATED)
def criar_barbeiro(payload: BarbeiroCreate, conn=Depends(get_db)):
    return barbeiro_service.criar_barbeiro(conn, payload)


@router.put("/{barbeiro_id}", response_model=BarbeiroResponse)
def atualizar_barbeiro(barbeiro_id: int, payload: BarbeiroUpdate, conn=Depends(get_db)):
    return barbeiro_service.atualizar_barbeiro(conn, barbeiro_id, payload)


@router.delete("/{barbeiro_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_barbeiro(barbeiro_id: int, conn=Depends(get_db)):
    barbeiro_service.deletar_barbeiro(conn, barbeiro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
