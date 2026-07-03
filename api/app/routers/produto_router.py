from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_db
from app.schemas.produto_schema import (
    HistoricoProdutoResponse,
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
)
from app.services import produto_service

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("", response_model=list[ProdutoResponse])
def listar_produtos(conn=Depends(get_db)):
    return produto_service.listar_produtos(conn)


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(produto_id: int, conn=Depends(get_db)):
    return produto_service.buscar_produto(conn, produto_id)


@router.get("/{produto_id}/historico", response_model=list[HistoricoProdutoResponse])
def listar_historico_produto(produto_id: int, conn=Depends(get_db)):
    return produto_service.listar_historico_produto(conn, produto_id)


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(payload: ProdutoCreate, conn=Depends(get_db)):
    return produto_service.criar_produto(conn, payload)


@router.put("/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, payload: ProdutoUpdate, conn=Depends(get_db)):
    return produto_service.atualizar_produto(conn, produto_id, payload)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_produto(produto_id: int, conn=Depends(get_db)):
    produto_service.deletar_produto(conn, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
