from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PessoaBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str = Field(min_length=11, max_length=11, pattern=r"^\d{11}$")
    email: str | None = Field(default=None, max_length=100)
    data_nascimento: date | None = None


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    cpf: str | None = Field(default=None, min_length=11, max_length=11, pattern=r"^\d{11}$")
    email: str | None = Field(default=None, max_length=100)
    data_nascimento: date | None = None


class PessoaResponse(PessoaBase):
    model_config = ConfigDict(from_attributes=True)

    id_pessoa: int
    created_at: datetime
    updated_at: datetime
