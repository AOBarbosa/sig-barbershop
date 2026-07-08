import pytest

from app.core import security


def test_hash_senha_gera_hash_diferente_da_senha_original():
    hash_ = security.hash_senha("minhasenha123")

    assert hash_ != "minhasenha123"
    assert hash_.startswith("$2b$")


def test_verificar_senha_aceita_senha_correta():
    hash_ = security.hash_senha("minhasenha123")

    assert security.verificar_senha("minhasenha123", hash_) is True


def test_verificar_senha_rejeita_senha_incorreta():
    hash_ = security.hash_senha("minhasenha123")

    assert security.verificar_senha("outrasenha", hash_) is False


def test_criar_e_decodificar_token_preserva_payload():
    token = security.criar_token({"sub": "1", "role": "admin"})

    dados = security.decodificar_token(token)

    assert dados["sub"] == "1"
    assert dados["role"] == "admin"
    assert "exp" in dados


def test_decodificar_token_invalido_lanca_erro():
    with pytest.raises(Exception):
        security.decodificar_token("token-invalido")


def test_decodificar_token_expirado_lanca_erro(monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "-1")

    token = security.criar_token({"sub": "1", "role": "admin"})

    with pytest.raises(Exception):
        security.decodificar_token(token)
