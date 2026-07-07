from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pessoa_schema import PessoaCreate, PessoaResponse


class ClienteCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    PESSOA_id_pessoa: int


class ClienteCompletoCreate(PessoaCreate):
    pass


class ClienteCompletoResponse(BaseModel):
    cliente: ClienteResponse
    pessoa: PessoaResponse
