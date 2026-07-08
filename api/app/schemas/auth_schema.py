from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["admin", "funcionario", "cliente"]


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=100)
    senha: str = Field(min_length=1, max_length=72)


class RegistroClienteRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str | None = Field(default=None, max_length=14)
    email: str = Field(min_length=1, max_length=100)
    data_nascimento: date | None = None
    senha: str = Field(min_length=6, max_length=72)
    preferencias: str | None = None
    observacoes: str | None = None


class UsuarioAtual(BaseModel):
    id_pessoa: int
    nome: str
    email: str | None = None
    role: Role
