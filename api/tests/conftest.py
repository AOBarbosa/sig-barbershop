import os

import mysql.connector
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from app.main import app

load_dotenv(".env.test", override=False)


@pytest.fixture(scope="function")
def db_conn():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        database=os.getenv("DB_NAME", "sig_barbershop_test"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
