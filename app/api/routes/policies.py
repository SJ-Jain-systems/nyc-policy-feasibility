from fastapi import APIRouter
from datetime import datetime

from app.db.duckdb_conn import get_conn
from app.services.nlp_service import extract_promises
from app.services.score_service import score_feasibility

router = APIRouter()

@router.post("/extract")
def extract_from_latest_source():
    with get_conn() as con:
        row = con.execute(
            "SELECT source_id, clean_text FROM sources ORDER BY fetched_at DESC LIMIT 1"
        ).fetchone()

    if not row:
        return {"ok": False, "error": "No sources found. POST /api/sources first."}

    source_id, clean_text = row
    promises = extract_promises(clean_text)

    inserted = 0
    with get_conn() as con:
        for item in promises:
            score, notes = score_feasibility(item["promise"], item["policy_area"])
            con.execute(
                """
                INSERT INTO policies (source_id, policy_area, promise, feasibility_score, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [source_id, item["policy_area"], item["promise"], score, notes, datetime.utcnow()]
            )
            inserted += 1

    return {"ok": True, "source_id": source_id, "inserted": inserted}

@router.get("")
def list_policies(limit: int = 25):
    with get_conn() as con:
        rows = con.execute(
            """
            SELECT policy_id, policy_area, promise, feasibility_score, notes
            FROM policies
            ORDER BY policy_id DESC
            LIMIT ?
            """,
            [limit]
        ).fetchall()

    return [
        {
            "policy_id": r[0],
            "policy_area": r[1],
            "promise": r[2],
            "feasibility_score": r[3],
            "notes": r[4],
        }
        for r in rows
    ]
