from pydantic import BaseModel, ConfigDict, Field


class FidelidadeBase(BaseModel):
    SERVICO_id_servico: int | None = None
    PRODUTO_id_produto: int | None = None
    pontos: int = Field(gt=0)
    ativo: bool = True


class FidelidadeCreate(FidelidadeBase):
    pass


class FidelidadeUpdate(BaseModel):
    SERVICO_id_servico: int | None = None
    PRODUTO_id_produto: int | None = None
    pontos: int | None = Field(default=None, gt=0)
    ativo: bool | None = None


class FidelidadeResponse(FidelidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id_fidelidade: int
