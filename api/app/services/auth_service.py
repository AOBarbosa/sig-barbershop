from fastapi import HTTPException

from app.core.security import criar_token, decodificar_token, hash_senha, verificar_senha
from app.repositories import barbeiro_repository, caixa_repository, cliente_repository, pessoa_repository
from app.schemas.auth_schema import LoginRequest, RegistroClienteRequest


def _derivar_role(conn, pessoa: dict) -> str:
    if pessoa.get("admin"):
        return "admin"
    if barbeiro_repository.buscar_por_pessoa(conn, pessoa["id_pessoa"]) is not None:
        return "funcionario"
    if caixa_repository.buscar_por_pessoa(conn, pessoa["id_pessoa"]) is not None:
        return "funcionario"
    if cliente_repository.buscar_por_pessoa(conn, pessoa["id_pessoa"]) is not None:
        return "cliente"
    raise HTTPException(status_code=403, detail="Pessoa sem papel de acesso definido")


def _usuario_dict(pessoa: dict, role: str) -> dict:
    return {
        "id_pessoa": pessoa["id_pessoa"],
        "nome": pessoa["nome"],
        "email": pessoa["email"],
        "role": role,
    }


def login(conn, payload: LoginRequest) -> tuple[str, dict]:
    pessoa = pessoa_repository.buscar_por_email(conn, payload.email)
    if pessoa is None or not pessoa.get("senha_hash"):
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    if not verificar_senha(payload.senha, pessoa["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha invalidos")

    role = _derivar_role(conn, pessoa)
    usuario = _usuario_dict(pessoa, role)
    token = criar_token({"sub": str(pessoa["id_pessoa"]), "role": role})
    return token, usuario


def registrar_cliente(conn, payload: RegistroClienteRequest) -> tuple[str, dict]:
    conn.start_transaction()
    try:
        if payload.cpf and pessoa_repository.buscar_por_cpf(conn, payload.cpf) is not None:
            raise HTTPException(status_code=409, detail="CPF ja cadastrado")
        if pessoa_repository.buscar_por_email(conn, payload.email) is not None:
            raise HTTPException(status_code=409, detail="Email ja cadastrado")

        pessoa = pessoa_repository.criar(
            conn,
            {
                "nome": payload.nome,
                "cpf": payload.cpf,
                "email": payload.email,
                "data_nascimento": payload.data_nascimento,
                "admin": False,
            },
        )
        pessoa_repository.atualizar_senha(conn, pessoa["id_pessoa"], hash_senha(payload.senha))
        cliente_repository.criar(
            conn,
            {
                "PESSOA_id_pessoa": pessoa["id_pessoa"],
                "preferencias": payload.preferencias,
                "observacoes": payload.observacoes,
            },
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise

    usuario = _usuario_dict(pessoa, "cliente")
    token = criar_token({"sub": str(pessoa["id_pessoa"]), "role": "cliente"})
    return token, usuario


def obter_usuario_atual(conn, token: str | None) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Nao autenticado")

    try:
        dados = decodificar_token(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado") from exc

    pessoa = pessoa_repository.buscar_por_id(conn, int(dados["sub"]))
    if pessoa is None:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")

    role = _derivar_role(conn, pessoa)
    return _usuario_dict(pessoa, role)
