from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AtendimentoStatus = Literal["agendado", "em_andamento", "concluido", "cancelado"]


class AtendimentoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_id_cliente: int = Field(gt=0)
    BARBEIRO_id_barbeiro: int = Field(gt=0)
    data_hora: datetime
    status: AtendimentoStatus = "agendado"
    observacao: str | None = None


class AtendimentoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_id_cliente: int | None = Field(default=None, gt=0)
    BARBEIRO_id_barbeiro: int | None = Field(default=None, gt=0)
    data_hora: datetime | None = None
    status: AtendimentoStatus | None = None
    observacao: str | None = None


class AtendimentoStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AtendimentoStatus


class AtendimentoServicoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    SERVICO_id_servico: int = Field(gt=0)


class AtendimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_atendimento: int
    CLIENTE_id_cliente: int
    BARBEIRO_id_barbeiro: int
    data_hora: datetime
    status: AtendimentoStatus
    valor_total: Decimal
    observacao: str | None = None


class AtendimentoServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_atendimento_servico: int
    ATENDIMENTO_id_atendimento: int
    SERVICO_id_servico: int
    preco_cobrado: Decimal
