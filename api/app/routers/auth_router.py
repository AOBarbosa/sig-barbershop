from fastapi import APIRouter, Depends, Request, Response, status

from app.core.security import COOKIE_NAME
from app.dependencies import get_db
from app.schemas.auth_schema import LoginRequest, RegistroClienteRequest, UsuarioAtual
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_cookie_auth(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
    )


@router.post("/login", response_model=UsuarioAtual)
def login(payload: LoginRequest, response: Response, conn=Depends(get_db)):
    token, usuario = auth_service.login(conn, payload)
    _set_cookie_auth(response, token)
    return usuario


@router.post(
    "/registrar-cliente", response_model=UsuarioAtual, status_code=status.HTTP_201_CREATED
)
def registrar_cliente(payload: RegistroClienteRequest, response: Response, conn=Depends(get_db)):
    token, usuario = auth_service.registrar_cliente(conn, payload)
    _set_cookie_auth(response, token)
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=UsuarioAtual)
def me(request: Request, conn=Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    return auth_service.obter_usuario_atual(conn, token)
