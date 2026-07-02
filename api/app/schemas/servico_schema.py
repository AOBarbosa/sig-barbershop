from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServicoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    descricao: str | None = None
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    duracao_minutos: int = Field(gt=0)
    ativo: bool = True


class ServicoCreate(ServicoBase):
    pass


class ServicoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = None
    preco: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    duracao_minutos: int | None = Field(default=None, gt=0)
    ativo: bool | None = None


class ServicoResponse(ServicoBase):
    model_config = ConfigDict(from_attributes=True)

    id_servico: int
