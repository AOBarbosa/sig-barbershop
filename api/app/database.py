import os

from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv()

_pool = None


def get_connection():
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(
            pool_name="barbershop",
            pool_size=5,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            database=os.getenv("DB_NAME", "sig_barbershop"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
        )
    return _pool.get_connection()
