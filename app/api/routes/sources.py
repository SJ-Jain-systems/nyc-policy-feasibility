from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

from app.db.duckdb_conn import get_conn
from app.services.ingest_service import fetch_and_clean, IngestError

router = APIRouter()

class SourceIn(BaseModel):
    url: str

@router.post("")
def add_source(payload: SourceIn):
    try:
        clean_text = fetch_and_clean(payload.url)
    except IngestError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        # catches anything unexpected so frontend always gets JSON
        return {"ok": False, "error": f"Unexpected ingest error: {type(e).__name__}: {e}"}

    fetched_at = datetime.utcnow()

    with get_conn() as con:
        con.execute(
            "INSERT INTO sources (url, fetched_at, clean_text) VALUES (?, ?, ?)",
            [payload.url, fetched_at, clean_text]
        )
        source_id = con.execute("SELECT max(source_id) FROM sources").fetchone()[0]

    return {"ok": True, "source_id": source_id, "chars": len(clean_text)}
