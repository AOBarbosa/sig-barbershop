import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

JWT_ALGORITHM = "HS256"
COOKIE_NAME = "access_token"


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token(payload: dict) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret-troque-em-producao-32-bytes+")
    minutos = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
    dados = payload | {"exp": datetime.now(timezone.utc) + timedelta(minutes=minutos)}
    return jwt.encode(dados, secret, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    secret = os.getenv("JWT_SECRET", "dev-secret-troque-em-producao-32-bytes+")
    return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
