from pydantic import BaseModel, ConfigDict, Field


class FidelidadeBase(BaseModel):
    SERVICO_id_servico: int | None = None
    PRODUTO_id_produto: int | None = None
    pontos_acumulados: int = Field(default=0, ge=0)
    pontos_uso: int = Field(default=0, ge=0)
    ativo: bool = True


class FidelidadeCreate(FidelidadeBase):
    pass


class FidelidadeUpdate(BaseModel):
    SERVICO_id_servico: int | None = None
    PRODUTO_id_produto: int | None = None
    pontos_acumulados: int | None = Field(default=None, ge=0)
    pontos_uso: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class FidelidadeResponse(FidelidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id_fidelidade: int
