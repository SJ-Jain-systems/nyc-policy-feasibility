import duckdb
from pathlib import Path

DB_PATH = Path("data/warehouse.duckdb")
SCHEMA_PATH = Path("app/db/schema.sql")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def init_db():
    with get_conn() as con:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        con.execute(schema_sql)
