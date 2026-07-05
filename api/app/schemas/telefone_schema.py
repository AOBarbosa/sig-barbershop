from pydantic import BaseModel, ConfigDict, Field


class TelefoneBase(BaseModel):
    numero: str = Field(min_length=11, max_length=11, pattern=r"^\d{11}$")


class TelefoneCreate(TelefoneBase):
    PESSOA_id_pessoa: int = Field(gt=0)


class TelefoneUpdate(BaseModel):
    numero: str | None = Field(default=None, min_length=11, max_length=11, pattern=r"^\d{11}$")


class TelefoneResponse(TelefoneBase):
    model_config = ConfigDict(from_attributes=True)

    id_telefone: int
    PESSOA_id_pessoa: int
