from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    categoria: str | None = Field(default=None, max_length=60)
    ativo: bool = True
    preco_venda: Decimal = Field(ge=0)
    preco_custo: Decimal = Field(ge=0)
    pontos_gerados: int = Field(default=0, ge=0)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=80)
    categoria: str | None = Field(default=None, max_length=60)
    ativo: bool | None = None
    preco_venda: Decimal | None = Field(default=None, ge=0)
    preco_custo: Decimal | None = Field(default=None, ge=0)
    pontos_gerados: int | None = Field(default=None, ge=0)


class ProdutoResponse(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id_produto: int
    preco_custo: Decimal | None = None


class HistoricoProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    PRODUTO_id_produto: int
    preco_venda: Decimal
    preco_custo: Decimal | None = None
    pontos_gerados: int
    data_inicio: date
    data_fim: date | None
    ativo: bool
