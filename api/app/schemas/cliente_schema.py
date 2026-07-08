from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pessoa_schema import PessoaCreate, PessoaResponse


class ClienteCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)
    preferencias: str | None = None
    observacoes: str | None = None


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    PESSOA_id_pessoa: int
    preferencias: str | None = None
    observacoes: str | None = None
    saldo_pontos: int = 0


class ClienteCompletoCreate(PessoaCreate):
    preferencias: str | None = None
    observacoes: str | None = None


class ClienteCompletoResponse(BaseModel):
    cliente: ClienteResponse
    pessoa: PessoaResponse
