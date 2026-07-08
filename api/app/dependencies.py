from fastapi import Depends, HTTPException, Request, status

from .core.security import COOKIE_NAME
from .database import get_connection
from .services import auth_service


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_current_user(request: Request, conn=Depends(get_db)) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    return auth_service.obter_usuario_atual(conn, token)


def get_current_user_opcional(request: Request, conn=Depends(get_db)) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return auth_service.obter_usuario_atual(conn, token)
    except HTTPException:
        return None


def require_admin(usuario: dict = Depends(get_current_user)) -> dict:
    if usuario["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a administradores")
    return usuario


def require_funcionario(usuario: dict = Depends(get_current_user)) -> dict:
    if usuario["role"] not in ("admin", "funcionario"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a funcionarios")
    return usuario


def require_cliente(usuario: dict = Depends(get_current_user)) -> dict:
    if usuario["role"] != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito a clientes")
    return usuario
