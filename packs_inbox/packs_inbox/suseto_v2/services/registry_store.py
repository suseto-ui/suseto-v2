import json, uuid, io, csv
from pathlib import Path
from datetime import datetime, timezone
DATA=Path(__file__).resolve().parent.parent/'data'/'registry.json'
VALID={'active','reserved','retired'}
def _load():
 DATA.parent.mkdir(parents=True,exist_ok=True)
 if not DATA.exists(): return {'profiles':[],'items':[]}
 try:return json.loads(DATA.read_text(encoding='utf-8'))
 except Exception:return {'profiles':[],'items':[]}
def _save(d):
 DATA.parent.mkdir(parents=True,exist_ok=True);DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def profiles():return _load()['profiles']
def items(q='',status=''):
 out=_load()['items'];q=q.strip().lower()
 return [x for x in out if (not status or x['status']==status) and (not q or q in (x['name']+' '+x['payload']+' '+x.get('tag','')).lower())]
def add_profile(d):
 x={'id':uuid.uuid4().hex[:10],'name':str(d.get('name','')).strip(),'kind':d.get('kind','qr'),'format':d.get('format','png'),'prefix':str(d.get('prefix','')).strip(),'created_at':now()}
 if not x['name']:raise ValueError('Název profilu je povinný.')
 data=_load();data['profiles'].append(x);_save(data);return x
def add_item(d):
 x={'id':uuid.uuid4().hex[:10],'name':str(d.get('name','')).strip(),'payload':str(d.get('payload','')).strip(),'tag':str(d.get('tag','')).strip(),'status':d.get('status','active'),'profile_id':str(d.get('profile_id','')),'created_at':now(),'updated_at':now()}
 if not x['name'] or not x['payload']:raise ValueError('Název i payload jsou povinné.')
 if x['status'] not in VALID:raise ValueError('Neplatný stav.')
 data=_load()
 if any(y['payload']==x['payload'] for y in data['items']):raise ValueError('Payload už je v registru.')
 data['items'].append(x);_save(data);return x
def set_status(item_id,status):
 if status not in VALID:raise ValueError('Neplatný stav.')
 data=_load()
 for x in data['items']:
  if x['id']==item_id:x['status']=status;x['updated_at']=now();_save(data);return x
 raise ValueError('Položka nebyla nalezena.')
def match(payload):
 for x in _load()['items']:
  if x['payload']==str(payload).strip():return x
 return None

def export_csv_text():
 out=io.StringIO(); w=csv.writer(out); w.writerow(['name','payload','tag','status','profile_id','created_at','updated_at'])
 for x in _load()['items']:w.writerow([x.get(k,'') for k in ['name','payload','tag','status','profile_id','created_at','updated_at']])
 return out.getvalue()
def import_csv_text(raw):
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))); data=_load(); added=[]; skipped=[]
 if not rows:raise ValueError('CSV je prázdné nebo nemá hlavičku.')
 known={x['payload'] for x in data['items']}
 for n,row in enumerate(rows,2):
  name=str(row.get('name','')).strip();payload=str(row.get('payload','')).strip();status=str(row.get('status','active')).strip()
  if not name or not payload:skipped.append({'row':n,'reason':'chybí název nebo payload'});continue
  if status not in VALID:skipped.append({'row':n,'reason':'neplatný stav'});continue
  if payload in known:skipped.append({'row':n,'reason':'duplicitní payload'});continue
  x={'id':uuid.uuid4().hex[:10],'name':name,'payload':payload,'tag':str(row.get('tag','')).strip(),'status':status,'profile_id':str(row.get('profile_id','')).strip(),'created_at':now(),'updated_at':now()};data['items'].append(x);known.add(payload);added.append(x)
 _save(data);return {'added':len(added),'skipped':skipped}
