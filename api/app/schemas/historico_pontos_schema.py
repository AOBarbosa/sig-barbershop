from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

TipoMovimentacao = Literal["ACUMULA", "USA"]


class HistoricoPontosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_movimentacao: int
    CLIENTE_PESSOA_id_pessoa: int
    VENDA_id_venda: int
    FIDELIDADE_id_fidelidade: int
    pontos: int
    tipo_movimentacao: TipoMovimentacao
    data_movimentacao: datetime


class SaldoPontosResponse(BaseModel):
    CLIENTE_PESSOA_id_pessoa: int
    saldo: int
