import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent/'data'; FILE=ROOT/'audit_log.json'
def _now(): return datetime.now(timezone.utc).isoformat()
def _load():
 try:return json.loads(FILE.read_text()) if FILE.exists() else []
 except Exception:return []
def write(action, actor='system', detail=''):
 data=_load(); data.insert(0,{'at':_now(),'action':action,'actor':actor,'detail':str(detail)[:300]}); ROOT.mkdir(exist_ok=True); FILE.write_text(json.dumps(data[:500],ensure_ascii=False,indent=2))
def list_entries(): return _load()[:200]
