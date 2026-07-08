from datetime import time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DiaSemana(str, Enum):
    segunda = "SEGUNDA"
    terca = "TERCA"
    quarta = "QUARTA"
    quinta = "QUINTA"
    sexta = "SEXTA"
    sabado = "SABADO"
    domingo = "DOMINGO"


class DisponibilidadeBase(BaseModel):
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fim: time
    ativo: bool = True

    @model_validator(mode="after")
    def _valida_intervalo(self):
        if self.hora_fim <= self.hora_inicio:
            raise ValueError("hora_fim deve ser posterior a hora_inicio")
        return self


class DisponibilidadeCreate(DisponibilidadeBase):
    BARBEIRO_PESSOA_id_pessoa: int = Field(gt=0)


class DisponibilidadeUpdate(BaseModel):
    dia_semana: DiaSemana | None = None
    hora_inicio: time | None = None
    hora_fim: time | None = None
    ativo: bool | None = None

    @model_validator(mode="after")
    def _valida_intervalo(self):
        if (
            self.hora_inicio is not None
            and self.hora_fim is not None
            and self.hora_fim <= self.hora_inicio
        ):
            raise ValueError("hora_fim deve ser posterior a hora_inicio")
        return self


class DisponibilidadeResponse(DisponibilidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id_disponibilidade: int
    BARBEIRO_PESSOA_id_pessoa: int
