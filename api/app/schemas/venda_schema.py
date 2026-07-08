from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

VendaStatus = Literal["ABERTA", "PAGA", "CANCELADA", "ESTORNADA"]
FormaPagamento = Literal["DINHEIRO", "PIX", "CARTAO_CREDITO", "CARTAO_DEBITO", "OUTRO"]


class VendaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_PESSOA_id_pessoa: int = Field(gt=0)
    CAIXA_PESSOA_id_pessoa: int = Field(gt=0)
    data_hora: datetime
    forma_pagamento: FormaPagamento
    desconto: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)


class VendaStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: VendaStatus


class VendaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_venda: int
    CLIENTE_PESSOA_id_pessoa: int
    CAIXA_PESSOA_id_pessoa: int
    data_hora: datetime
    valor_total: Decimal
    status: VendaStatus
    forma_pagamento: FormaPagamento
    desconto: Decimal = Decimal("0.00")


class VendaProdutoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    PRODUTO_id_produto: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class VendaProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    VENDA_id_venda: int
    PRODUTO_id_produto: int
    quantidade: int
    preco_unitario: Decimal
