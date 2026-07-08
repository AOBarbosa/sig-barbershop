from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_current_user_opcional, get_db, require_funcionario
from app.schemas.produto_schema import (
    HistoricoProdutoResponse,
    ProdutoCreate,
    ProdutoResponse,
    ProdutoUpdate,
)
from app.services import produto_service

router = APIRouter(prefix="/produtos", tags=["produtos"])


def _ocultar_preco_custo(produto: dict, usuario: dict | None) -> dict:
    if usuario and usuario["role"] == "admin":
        return produto
    return produto | {"preco_custo": None}


@router.get("", response_model=list[ProdutoResponse])
def listar_produtos(usuario=Depends(get_current_user_opcional), conn=Depends(get_db)):
    produtos = produto_service.listar_produtos(conn)
    return [_ocultar_preco_custo(p, usuario) for p in produtos]


@router.get("/{produto_id}", response_model=ProdutoResponse)
def buscar_produto(
    produto_id: int, usuario=Depends(get_current_user_opcional), conn=Depends(get_db)
):
    produto = produto_service.buscar_produto(conn, produto_id)
    return _ocultar_preco_custo(produto, usuario)


@router.get("/{produto_id}/historico", response_model=list[HistoricoProdutoResponse])
def listar_historico_produto(
    produto_id: int, usuario=Depends(get_current_user_opcional), conn=Depends(get_db)
):
    historico = produto_service.listar_historico_produto(conn, produto_id)
    return [_ocultar_preco_custo(h, usuario) for h in historico]


@router.post(
    "",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_funcionario)],
)
def criar_produto(payload: ProdutoCreate, conn=Depends(get_db)):
    return produto_service.criar_produto(conn, payload)


@router.put(
    "/{produto_id}", response_model=ProdutoResponse, dependencies=[Depends(require_funcionario)]
)
def atualizar_produto(produto_id: int, payload: ProdutoUpdate, conn=Depends(get_db)):
    return produto_service.atualizar_produto(conn, produto_id, payload)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_funcionario)],
)
def deletar_produto(produto_id: int, conn=Depends(get_db)):
    produto_service.deletar_produto(conn, produto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
