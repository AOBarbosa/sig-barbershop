from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.produto_router import router as produto_router
from app.routers.servico_router import router as servico_router

app = FastAPI(title="SIG Barbershop API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(servico_router)
app.include_router(produto_router)


@app.get("/health")
def health():
    return {"status": "ok"}
