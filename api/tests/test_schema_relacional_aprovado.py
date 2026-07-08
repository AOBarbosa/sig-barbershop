from pathlib import Path
import re


SCHEMA_SQL = Path(__file__).resolve().parents[1] / "app" / "db" / "schema.sql"


def test_schema_usa_chaves_relacionais_aprovadas():
    schema = SCHEMA_SQL.read_text()

    assert re.search(r"PESSOA_id_pessoa\s+INT\s+NOT NULL PRIMARY KEY", schema)
    assert "CLIENTE_PESSOA_id_pessoa" in schema
    assert "BARBEIRO_PESSOA_id_pessoa" in schema
    assert "CAIXA_PESSOA_id_pessoa" in schema
    assert "id_cliente" not in schema
    assert "id_barbeiro" not in schema
    assert "id_caixa" not in schema


def test_schema_reflete_campos_do_modelo_relacional_aprovado():
    schema = SCHEMA_SQL.read_text()

    assert re.search(r"apelido\s+VARCHAR\(60\)", schema)
    assert re.search(r"comissao_percentual\s+DECIMAL\(5,2\)", schema)
    assert re.search(r"data_hora_inicio\s+DATETIME\s+NOT NULL", schema)
    assert re.search(r"data_hora_fim\s+DATETIME", schema)
    assert re.search(r"pontos_acumulados\s+INT\s+NOT NULL", schema)
    assert re.search(r"pontos_uso\s+INT\s+NOT NULL", schema)
    assert re.search(r"id_movimentacao\s+INT\s+NOT NULL AUTO_INCREMENT", schema)
    assert "especialidade" not in schema
    assert "duracao_minutos" not in schema
    assert "estoque" not in schema
