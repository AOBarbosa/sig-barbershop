from pydantic import BaseModel, ConfigDict, Field


class TelefoneBase(BaseModel):
    telefone: str = Field(min_length=1, max_length=20)


class TelefoneCreate(TelefoneBase):
    PESSOA_id_pessoa: int = Field(gt=0)


class TelefoneUpdate(BaseModel):
    telefone: str | None = Field(default=None, min_length=1, max_length=20)


class TelefoneResponse(TelefoneBase):
    model_config = ConfigDict(from_attributes=True)

    PESSOA_id_pessoa: int
