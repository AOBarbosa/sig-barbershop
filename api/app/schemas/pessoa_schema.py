from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PessoaBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str | None = Field(default=None, max_length=14)
    email: str | None = Field(default=None, max_length=100)
    data_nascimento: date | None = None
    admin: bool = False


class PessoaCreate(PessoaBase):
    pass


class PessoaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    cpf: str | None = Field(default=None, max_length=14)
    email: str | None = Field(default=None, max_length=100)
    data_nascimento: date | None = None
    admin: bool | None = None


class PessoaResponse(PessoaBase):
    model_config = ConfigDict(from_attributes=True)

    id_pessoa: int
