from pydantic import BaseModel, ConfigDict, Field


class ClienteCreate(BaseModel):
    PESSOA_id_pessoa: int = Field(gt=0)


class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: int
    PESSOA_id_pessoa: int
