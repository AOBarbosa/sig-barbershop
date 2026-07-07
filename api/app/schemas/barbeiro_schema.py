from pydantic import BaseModel, ConfigDict, Field

from app.schemas.pessoa_schema import PessoaCreate, PessoaResponse, PessoaUpdate


class BarbeiroCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)
    especialidade: str | None = Field(default=None, max_length=100)
    ativo: bool = True


class BarbeiroUpdate(BaseModel):
    especialidade: str | None = Field(default=None, max_length=100)
    ativo: bool | None = None


class BarbeiroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_barbeiro: int
    PESSOA_id_pessoa: int
    especialidade: str | None
    ativo: bool


class BarbeiroCompletoCreate(PessoaCreate):
    especialidade: str | None = Field(default=None, max_length=100)
    ativo: bool = True


class BarbeiroCompletoUpdate(PessoaUpdate):
    especialidade: str | None = Field(default=None, max_length=100)
    ativo: bool | None = None


class BarbeiroCompletoResponse(BaseModel):
    barbeiro: BarbeiroResponse
    pessoa: PessoaResponse
