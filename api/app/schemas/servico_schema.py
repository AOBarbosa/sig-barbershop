from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    ativo: bool = True
    preco: Decimal = Field(ge=0)
    duracao_em_minutos: int = Field(gt=0)
    pontos_gerados: int = Field(default=0, ge=0)


class ServicoCreate(ServicoBase):
    pass


class ServicoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=80)
    ativo: bool | None = None
    preco: Decimal | None = Field(default=None, ge=0)
    duracao_em_minutos: int | None = Field(default=None, gt=0)
    pontos_gerados: int | None = Field(default=None, ge=0)


class ServicoResponse(ServicoBase):
    model_config = ConfigDict(from_attributes=True)

    id_servico: int


class HistoricoServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    SERVICO_id_servico: int
    preco: Decimal
    duracao_em_minutos: int
    pontos_gerados: int
    data_inicio: date
    data_fim: date | None
    ativo: bool
