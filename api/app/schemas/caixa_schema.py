from pydantic import BaseModel, ConfigDict, Field


class CaixaCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)


class CaixaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    PESSOA_id_pessoa: int
