from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

TipoMovimentacao = Literal["acumulo", "resgate"]


class HistoricoPontosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_historico: int
    CLIENTE_id_cliente: int
    pontos: int
    tipo_movimentacao: TipoMovimentacao
    descricao: str | None = None
    data_movimentacao: datetime


class SaldoPontosResponse(BaseModel):
    CLIENTE_id_cliente: int
    saldo: int
