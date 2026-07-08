from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AtendimentoStatus = Literal["AGENDADO", "EM_EXECUCAO", "CONCLUIDO", "CANCELADO"]


class AtendimentoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_PESSOA_id_pessoa: int = Field(gt=0)
    BARBEIRO_PESSOA_id_pessoa: int = Field(gt=0)
    data_hora_inicio: datetime
    data_hora_fim: datetime | None = None
    status: AtendimentoStatus = "AGENDADO"
    observacoes: str | None = None


class AtendimentoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    CLIENTE_PESSOA_id_pessoa: int | None = Field(default=None, gt=0)
    BARBEIRO_PESSOA_id_pessoa: int | None = Field(default=None, gt=0)
    data_hora_inicio: datetime | None = None
    data_hora_fim: datetime | None = None
    status: AtendimentoStatus | None = None
    observacoes: str | None = None


class AtendimentoStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AtendimentoStatus


class AtendimentoServicoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    SERVICO_id_servico: int = Field(gt=0)


class AtendimentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_atendimento: int
    CLIENTE_PESSOA_id_pessoa: int
    BARBEIRO_PESSOA_id_pessoa: int
    data_hora_inicio: datetime
    data_hora_fim: datetime | None = None
    status: AtendimentoStatus
    valor_total: Decimal
    observacoes: str | None = None


class AtendimentoServicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ATENDIMENTO_id_atendimento: int
    SERVICO_id_servico: int
    preco_cobrado: Decimal
