from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

VendaStatus = Literal["pendente", "concluida", "cancelada"]
FormaPagamento = Literal["dinheiro", "cartao_debito", "cartao_credito", "pix"]


class VendaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_id_cliente: int = Field(gt=0)
    CAIXA_id_caixa: int = Field(gt=0)
    forma_pagamento: FormaPagamento | None = None


class VendaStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: VendaStatus


class VendaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_venda: int
    CLIENTE_id_cliente: int
    CAIXA_id_caixa: int
    data_venda: datetime
    valor_total: Decimal
    status: VendaStatus
    forma_pagamento: FormaPagamento | None = None
