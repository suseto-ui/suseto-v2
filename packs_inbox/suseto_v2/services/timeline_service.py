import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent/'data'; FILE=ROOT/'asset_timeline.json'
def _now(): return datetime.now(timezone.utc).isoformat()
def _load():
 try:return json.loads(FILE.read_text()) if FILE.exists() else []
 except Exception:return []
def _save(data): ROOT.mkdir(exist_ok=True); FILE.write_text(json.dumps(data[:1000],ensure_ascii=False,indent=2))
def add(asset_key,action,actor='system',detail=''):
 data=_load(); data.insert(0,{'asset_key':asset_key,'action':action,'actor':actor,'detail':detail,'at':_now()}); _save(data)
def list_for(asset_key=None):
 data=_load(); return [x for x in data if not asset_key or x['asset_key']==asset_key][:200]
