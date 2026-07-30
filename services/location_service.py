import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent/'data'; FILE=ROOT/'locations.json'
def _now(): return datetime.now(timezone.utc).isoformat()
def _load():
 try:return json.loads(FILE.read_text()) if FILE.exists() else {'locations':[]}
 except Exception:return {'locations':[]}
def _save(data): ROOT.mkdir(exist_ok=True); FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2))
def list_locations(): return _load()['locations']
def add_location(name,building='',room='',shelf='',slot=''):
 data=_load(); row={'id':datetime.now().strftime('%Y%m%d%H%M%S%f'),'name':name,'building':building,'room':room,'shelf':shelf,'slot':slot,'created_at':_now()}; data['locations'].insert(0,row); _save(data); return row
