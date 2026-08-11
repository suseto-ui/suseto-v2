from pathlib import Path
import json, uuid, datetime
STORE=Path(__file__).resolve().parent.parent / "data" / "runs.json"
def _read():
    try: return json.loads(STORE.read_text())
    except Exception: return []
def save_run(record):
    rows=_read(); record={"id":uuid.uuid4().hex[:10],"created_at":datetime.datetime.now(datetime.UTC).isoformat(),**record}; rows.insert(0,record); STORE.parent.mkdir(exist_ok=True); STORE.write_text(json.dumps(rows[:50],ensure_ascii=False,indent=2)); return record
def list_runs(): return _read()[:20]
def get_run(run_id): return next((r for r in _read() if r.get("id")==run_id),None)
