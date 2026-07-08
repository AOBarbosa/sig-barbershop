from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pessoa_schema import PessoaCreate, PessoaResponse, PessoaUpdate


class BarbeiroCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)
    apelido: str | None = Field(default=None, max_length=60)
    comissao_percentual: float | None = None


class BarbeiroUpdate(BaseModel):
    apelido: str | None = Field(default=None, max_length=60)
    comissao_percentual: float | None = None


class BarbeiroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    PESSOA_id_pessoa: int
    apelido: str | None
    comissao_percentual: float | None


class BarbeiroCompletoCreate(PessoaCreate):
    apelido: str | None = Field(default=None, max_length=60)
    comissao_percentual: float | None = None


class BarbeiroCompletoUpdate(PessoaUpdate):
    apelido: str | None = Field(default=None, max_length=60)
    comissao_percentual: float | None = None


class BarbeiroCompletoResponse(BaseModel):
    barbeiro: BarbeiroResponse
    pessoa: PessoaResponse
