from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    descricao: str | None = None
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    estoque: int = Field(ge=0)
    ativo: bool = True


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = None
    preco: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    estoque: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class ProdutoResponse(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id_produto: int


class HistoricoProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    PRODUTO_id_produto: int
    preco_anterior: Decimal | None
    preco_novo: Decimal | None
    estoque_anterior: int | None
    estoque_novo: int | None
    ativo: bool
    alterado_em: datetime
