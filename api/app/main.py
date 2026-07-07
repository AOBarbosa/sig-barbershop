from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.atendimento_router import router as atendimento_router
from app.routers.barbeiro_router import router as barbeiro_router
from app.routers.caixa_router import router as caixa_router
from app.routers.cliente_router import router as cliente_router
from app.routers.disponibilidade_router import router as disponibilidade_router
from app.routers.fidelidade_router import router as fidelidade_router
from app.routers.historico_pontos_router import router as historico_pontos_router
from app.routers.pessoa_router import router as pessoa_router
from app.routers.produto_router import router as produto_router
from app.routers.servico_router import router as servico_router
from app.routers.telefone_router import router as telefone_router
from app.routers.venda_router import router as venda_router

app = FastAPI(title="SIG Barbershop API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pessoa_router)
app.include_router(telefone_router)
app.include_router(cliente_router)
app.include_router(caixa_router)
app.include_router(barbeiro_router)
app.include_router(disponibilidade_router)
app.include_router(servico_router)
app.include_router(produto_router)
app.include_router(atendimento_router)
app.include_router(fidelidade_router)
app.include_router(venda_router)
app.include_router(historico_pontos_router)


@app.get("/health")
def health():
    return {"status": "ok"}
